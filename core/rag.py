from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_llm
from core.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from core.vector_store import search_foods


def format_context(foods):
    lines = []
    for i, f in enumerate(foods, start=1):
        lines.append(
            f"[{i}] {f['name']}: {f['calories']} kcal, {f['protein']}g protein, "
            f"{f['carbs']}g carbs, {f['fat']}g fat, diet: {f['diet']} "
            f"(source: {f['source']})"
        )
    return "\n".join(lines)


def answer_question(question, diet=None, k=5):
    foods = search_foods(question, k=k, diet=diet)
    context = format_context(foods)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=USER_TEMPLATE.format(context=context, question=question)),
    ]
    response = get_llm().invoke(messages)
    return {"answer": response.content, "sources": foods}