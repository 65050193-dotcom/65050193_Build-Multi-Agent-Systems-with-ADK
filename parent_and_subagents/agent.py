import os
from dotenv import load_dotenv

from google.genai import types
from google.adk.models import Gemini

from google.adk.agents import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.loop_agent import LoopAgent

from google.adk.tools import exit_loop
from google.adk.tools.tool_context import ToolContext

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


# =========================================================
# ENV / MODEL
# =========================================================
load_dotenv()
MODEL_NAME = os.getenv("MODEL", "gemini-1.5-flash")

RETRY_OPTIONS = types.HttpRetryOptions(initial_delay=1, attempts=6)

# =========================================================
# Wikipedia (Real tool)
# =========================================================
_wiki_runner = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=3,
        doc_content_chars_max=1600,
    )
)

def wikipedia_search(query: str) -> str:
    """Search Wikipedia (real) and return a text summary."""
    return _wiki_runner.run(query)


# =========================================================
# State tools (ToolContext)
# =========================================================
def init_defaults(tool_context: ToolContext) -> str:
    tool_context.state.setdefault("topic", "")
    tool_context.state.setdefault("pos_data", "")
    tool_context.state.setdefault("neg_data", "")
    tool_context.state.setdefault("pos_keywords", "achievements legacy reforms contributions impact")
    tool_context.state.setdefault("neg_keywords", "controversy criticism allegations human rights criticism")
    tool_context.state.setdefault("loop_count", 0)
    tool_context.state.setdefault("max_loops", 3)
    tool_context.state.setdefault("pos_count", 0)
    tool_context.state.setdefault("neg_count", 0)
    tool_context.state.setdefault("verdict_text", "")
    return "Initialized defaults."

def set_state(tool_context: ToolContext, key: str, value: str) -> str:
    tool_context.state[key] = value
    return f"Saved state[{key}]"

def bump_loop(tool_context: ToolContext) -> str:
    tool_context.state["loop_count"] = int(tool_context.state.get("loop_count", 0)) + 1
    return f"loop_count={tool_context.state['loop_count']}"

def refine_keywords(tool_context: ToolContext, side: str) -> str:
    """Refine search keywords when one side lacks enough points."""
    if side == "pos":
        extra = " awards influence leadership accomplishments major works philanthropy reforms"
        tool_context.state["pos_keywords"] = (tool_context.state.get("pos_keywords", "") + extra).strip()
        return "Refined pos_keywords."
    if side == "neg":
        extra = " war crimes massacre corruption political repression opposition failures backlash"
        tool_context.state["neg_keywords"] = (tool_context.state.get("neg_keywords", "") + extra).strip()
        return "Refined neg_keywords."
    return "Unknown side."

def _count_bullets(text: str) -> int:
    if not text:
        return 0
    return sum(1 for line in text.splitlines() if line.strip().startswith("- "))

def check_balance(tool_context: ToolContext) -> str:
    pos = tool_context.state.get("pos_data", "")
    neg = tool_context.state.get("neg_data", "")
    tool_context.state["pos_count"] = _count_bullets(pos)
    tool_context.state["neg_count"] = _count_bullets(neg)
    return f"pos_count={tool_context.state['pos_count']}, neg_count={tool_context.state['neg_count']}"


# =========================================================
# Save verdict
# =========================================================
def save_verdict(text: str) -> str:
    with open("verdict.txt", "w", encoding="utf-8") as f:
        f.write(text)
    return "Verdict saved to verdict.txt"


# =========================================================
# Step 0: Initializer
# =========================================================
initializer = Agent(
    name="initializer",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    tools=[init_defaults],
    instruction="""
Call init_defaults tool exactly once.
Then output ONLY: OK
"""
)


# =========================================================
# Step 1: Inquiry (validate historical topic)
# =========================================================
inquiry_agent = Agent(
    name="inquiry_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    tools=[set_state],
    instruction="""
Ask the user to provide ONE historical person OR ONE historical event.

Validation:
- If user gives a modern celebrity/athlete/influencer or a person likely still alive,
  ask them to choose a HISTORICAL topic instead (e.g., Napoleon, Julius Caesar, World War II, Cold War).
  Do NOT call set_state.

If valid:
- Extract ONLY the topic phrase.
- Call set_state(key="topic", value="<topic>")
"""
)


# =========================================================
# Step 2: Parallel Investigation
#   - Use set_state per round (avoid duplicates)
# =========================================================
admirer_agent = Agent(
    name="admirer_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    tools=[wikipedia_search, set_state],
    instruction="""
You are Agent A (The Admirer). Collect ONLY positive aspects.

1) Use wikipedia_search AT LEAST 3 times with:
   - "{topic?} achievements"
   - "{topic?} legacy"
   - "{topic?} {pos_keywords?}"

2) Create AT LEAST 3 DISTINCT positive points.
   Output as bullets, each line starts with "- ".

3) Call:
   set_state(key="pos_data", value="<bullets only>")
"""
)

critic_agent = Agent(
    name="critic_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    tools=[wikipedia_search, set_state],
    instruction="""
You are Agent B (The Critic). Collect ONLY negative/controversial aspects.

1) Use wikipedia_search AT LEAST 3 times with:
   - "{topic?} controversy"
   - "{topic?} criticism"
   - "{topic?} {neg_keywords?}"

2) Create AT LEAST 3 DISTINCT negative/controversial points.
   Output as bullets, each line starts with "- ".

3) Call:
   set_state(key="neg_data", value="<bullets only>")
"""
)

parallel_investigation = ParallelAgent(
    name="parallel_investigation",
    sub_agents=[admirer_agent, critic_agent]
)


# =========================================================
# Step 3: Judge loop (must exit via exit_loop tool only)
# =========================================================
judge_agent = Agent(
    name="judge_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    tools=[check_balance, bump_loop, refine_keywords, exit_loop],
    instruction="""
You are Agent C (The Judge).

1) Call check_balance().

2) Print status EXACTLY:
JUDGE_STATUS: pos={pos_count?}, neg={neg_count?}, loop={loop_count?}/{max_loops?}

3) If pos_count >= 3 AND neg_count >= 3:
     Call exit_loop()

4) Otherwise:
     Call bump_loop()
     If loop_count < max_loops:
        - If pos_count < 3: call refine_keywords(side="pos")
        - If neg_count < 3: call refine_keywords(side="neg")
        Do NOT call exit_loop (let loop run again)
     Else:
        Call exit_loop() to prevent infinite loop
"""
)

review_loop = LoopAgent(
    name="review_loop",
    sub_agents=[parallel_investigation, judge_agent]
)


# =========================================================
# Step 4: Verdict writer -> store verdict_text in state
# =========================================================
verdict_writer = Agent(
    name="verdict_writer",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    tools=[set_state],
    instruction="""
Write a balanced comparative report using:

POSITIVE:
{pos_data?}

NEGATIVE:
{neg_data?}

Rules:
- Neutral tone, do NOT take sides, do NOT declare a winner.
- Structure:
  1) Intro (2-4 sentences)
  2) Key Achievements / Positive Contributions (bullets)
  3) Criticisms / Controversies (bullets)
  4) Balanced Assessment (2-4 paragraphs)
  5) Conclusion (neutral)

After you finish the full report, call:
set_state(key="verdict_text", value="<FULL REPORT>")
"""
)


# =========================================================
# Step 5: Saver (force save to file)
# =========================================================
verdict_saver = Agent(
    name="verdict_saver",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_OPTIONS),
    tools=[save_verdict],
    instruction="""
Call save_verdict with EXACTLY {verdict_text?}.
Then stop.
"""
)


# =========================================================
# ROOT AGENT (required name)
# =========================================================
root_agent = SequentialAgent(
    name="historical_court",
    sub_agents=[
        initializer,
        inquiry_agent,
        review_loop,
        verdict_writer,
        verdict_saver,
    ],
)