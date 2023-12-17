from langchain.schema.output_parser import StrOutputParser
from transformers import AutoTokenizer
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.prompts import PromptTemplate


# Create chain
# model = "ai-forever/rugpt3small_based_on_gpt2"
model = "AlexWortega/instruct_rugptSmall"
tokenizer = AutoTokenizer.from_pretrained(model)
rugpt = HuggingFacePipeline.from_model_id(
    # The name of the model on the HuggingFace server (for example "gpt2" by default) or the path to the model on disk
    # model_id="gpt2",
    model_id=model,
    # Other options are possible: "text2text-generation", "text-generation" (default), "summarization"
    task="text-generation",
    # task="text2text-generation",
    # Settings available for the model
    device=-1,
    # pipeline_kwargs={"max_new_tokens": 10},
    pipeline_kwargs={
        "temperature": 0.01,
        "max_length": 300,
        "repetition_penalty": 1.2,
        "do_sample": True,
        "top_k": 5,
        "top_p": 0.95,
    },
)

template = "{question}"
prompt = PromptTemplate(template=template, input_variables=["question"])
output_parser = StrOutputParser()

chain = prompt | rugpt | output_parser
