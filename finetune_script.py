
import torch
from unsloth import FastLanguageModel
from datasets import Dataset
import json

# Model yükleme
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/mistral-7b-instruct-v0.2-bnb-4bit",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# LoRA adaptörü ekle
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                   "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

# Training verilerini yükle
with open('alpaca_training_data.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)

dataset = Dataset.from_list(train_data)

def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs = examples["input"]
    outputs = examples["output"]
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        text = f"""Sen bir Türk Telekom çağrı merkezi temsilcisisin.

Müşteri: {instruction}
Temsilci: {output}"""
        texts.append(text)
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)

from trl import SFTTrainer
from transformers import TrainingArguments

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    dataset_num_proc=2,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=50,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
        save_steps=25,
    ),
)

# Training başlat
print("🚀 Fine-tuning başlatılıyor...")
trainer.train()

# Model kaydet
model.save_pretrained("teknofest_finetuned_model")
tokenizer.save_pretrained("teknofest_finetuned_model")

print("✅ Fine-tuning tamamlandı!")
print("📁 Model kaydedildi: teknofest_finetuned_model/")
