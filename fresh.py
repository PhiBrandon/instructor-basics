import instructor
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Literal


load_dotenv()


client = instructor.from_anthropic(Anthropic())


class ClassifyOutput(BaseModel):
    explanation: str
    classification: Literal["BEST", "MID", "WORST"]


class ListOutput(BaseModel):
    explanation: str
    email_lists: list[Literal["Cat List", "Dog List", "Albatross List"]]


customer_information = "Brandon loves Albatrosses but isn't very fond of dogs."
business = "Dog store that sells dog toys"
prompt = """
Classify the customer's likliness to buy from the business based on the customer information and the business.
Customer Information:
{customer_information}
Business:
{business}
""".format(
    customer_information=customer_information, business=business
)


resp, raw = client.chat.completions.create_with_completion(
    model="claude-3-haiku-20240307",
    messages=[{"role": "user", "content": prompt}],
    response_model=ClassifyOutput,
    max_tokens=4000,
)

assert isinstance(resp, ClassifyOutput), "Not the correct output type"
print(resp.explanation)
print(resp.classification)
print(raw)


list_prompt = """
Determine the correct email lists that the customer should be added to based on the classification and the business.
Classification:
{classification}
Business:
{business}
""".format(
    classification=resp, business=business
)

list_resp, list_raw = client.chat.completions.create_with_completion(
    model="claude-3-haiku-20240307",
    messages=[{"role": "user", "content": prompt}],
    response_model=ListOutput,
    max_tokens=4000,
)

assert isinstance(list_resp, ListOutput), f"Not the correct output type. Expected ListOutput"
print(list_resp.explanation)
print(list_resp.email_lists)
print(list_raw)