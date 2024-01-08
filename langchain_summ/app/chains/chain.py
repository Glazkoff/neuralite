from langchain.schema.output_parser import StrOutputParser
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)
import torch

ADAPTER_PATH = "/code/langchain_summ/models/Mistral_dialogsum_v2"
tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
device_map = "auto"
model = AutoModelForCausalLM.from_pretrained(
    ADAPTER_PATH,
    quantization_config=bnb_config,
    device_map=device_map,
)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=400)
hfp = HuggingFacePipeline(pipeline=pipe)

template = """Context:
{context} 
    
[INST]Summarizing the following text:[/INST]
Output:"""
prompt = PromptTemplate(template=template, input_variables=["context"])
output_parser = StrOutputParser()

chain = prompt | hfp | output_parser
