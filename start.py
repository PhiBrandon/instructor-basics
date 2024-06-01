from pydantic import BaseModel
import instructor
from anthropic import Anthropic
from typing import Literal
from dotenv import load_dotenv
import json
from fastapi import FastAPI

load_dotenv()


class ClassificationOutput(BaseModel):
    explanation: str
    classification: Literal["MID", "WORST", "BEST"]


class ListOutput(BaseModel):
    explanation: str
    email_lists: list[
        Literal[
            "CAT LIST",
            "DOG LIST",
            "PARROT LIST",
            "REPTILE LIST",
            "EXOTIC PET LIST",
            "FISH LIST",
        ]
    ]


class Example(BaseModel):
    customer_information: str
    industry: str
    email_lists: list[str]


client = instructor.from_anthropic(Anthropic())




def run_test(ClassificationOutput, ListOutput, client, example: Example):
    print(f"++++++++++++++++++++++++++++")
    print(f"Starting example: {example}")
    customer_information = example.customer_information
    industry = example.industry
    prompt = """
    Given the industry and customer information classify the customer's likelihood to buy from the industry store.
    Customer Information:
    {customer_information}
    Industry:
    {industry}
    """.format(
            customer_information=customer_information, industry=industry
        )

    resp, raw = client.chat.completions.create_with_completion(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
        response_model=ClassificationOutput,
    )

    assert isinstance(resp, ClassificationOutput), f"ERROR: Not Classification Output"
    print(resp.classification)

    list_prompt = """
    Given the classification information and the industry, recommend email lists that the customer could be added to based
    on the classification.
    Classification:
    {classification}
    Industry:
    {industry}
    """.format(
            classification=resp, industry=industry
        )

    list_resp, list_raw = client.chat.completions.create_with_completion(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        messages=[{"role": "user", "content": list_prompt}],
        response_model=ListOutput,
    )

    assert isinstance(list_resp, ListOutput), f"ERROR: Not List Output"

    print(list_resp.email_lists)
    correct = example.email_lists[0]
    assert (q
        correct in list_resp.email_lists
    ), f"ERROR: Does not contain {correct}. Instead {list_resp.email_lists}"
    print(f"EXAMPLE COMPLETE - PASS")
    print(f"++++++++++++++++++++++++++++\n\n")

file_test = open("examples.json", "r").read()
examples_json = json.loads(file_test)

correct = 0
for e in examples_json:
    curr_example = Example(**e)
    try:
        run_test(ClassificationOutput, ListOutput, client, curr_example)
        correct +=1
    except Exception as e:
        print(e)

print(f"\n\n================================\n")
print(f"FINISHED!")
print(f"Ratio: {correct}/{len(examples_json)}")
