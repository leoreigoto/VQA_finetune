import gradio as gr
import os
import torch
from PIL import Image
from peft import PeftConfig, PeftModel
from transformers import AutoProcessor, Blip2ForConditionalGeneration
from transformers import pipeline

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-2.7b")

peft_model_id = "leoreigoto/Data2_V2_BLIP2_Finetune_Caption_First_Epoch"
config = PeftConfig.from_pretrained(peft_model_id)
blip_finetune = Blip2ForConditionalGeneration.from_pretrained(config.base_model_name_or_path)#, load_in_8bit=True, device_map="auto")
blip_finetune = PeftModel.from_pretrained(blip_finetune, peft_model_id)

qa_model = pipeline("question-answering", "timpal0l/mdeberta-v3-base-squad2")


def generate_caption(pred_image):
  
    inputs = processor(pred_image,  return_tensors="pt").to(device, torch.float16)
    generated_ids = blip_finetune.generate(**inputs, max_new_tokens=50)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    return generated_text


def prompt_run(pred_image,prompt_box):
    generated_text = generate_caption(pred_image)
    generated_text = qa_model(question = prompt_box, context = generated_text)
    return generated_text['answer']



with gr.Blocks() as gradio_app:
  with gr.Row():
    pred_image = gr.Image(height=480,width= 480,image_mode='RGB',type="pil")
    with gr.Column():
      button_caption = gr.Button(value='Get image caption (description)',size='sm')
      prompt_box = gr.Textbox(label="Prompt",placeholder='enter prompt here')
      button_prompt = gr.Button(value='Run prompt',size='sm')
  with gr.Column():
    output_box = gr.Textbox(label="Model output", placeholder='model output')

    button_prompt.click(prompt_run,inputs=[pred_image,prompt_box], outputs=[output_box])
    button_caption.click(generate_caption,inputs=[pred_image], outputs=[output_box])

gradio_app.launch()

