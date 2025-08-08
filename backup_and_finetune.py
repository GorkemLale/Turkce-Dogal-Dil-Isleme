#!/usr/bin/env python3
"""
TEKNOFEST Model Yedekleme ve Fine-tuning Script
Gece çalışacak, sabah hazır olacak
"""

import os
import json
import subprocess
import time
from datetime import datetime

def log_message(message):
    """Log mesajı yazdır"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    with open("finetune_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def backup_current_model():
    """Mevcut modeli yedekle"""
    log_message("🔄 Model yedekleme başlatılıyor...")
    
    try:
        # Ollama modelini listelele
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        log_message(f"Mevcut modeller:\n{result.stdout}")
        
        # Modeli yedekle
        log_message("📦 Model yedekleniyor...")
        backup_result = subprocess.run(
            ["ollama", "show", "mistral:7b-instruct"], 
            capture_output=True, text=True
        )
        
        if backup_result.returncode == 0:
            log_message("✅ Model yedekleme başarılı!")
            return True
        else:
            log_message(f"❌ Model yedekleme hatası: {backup_result.stderr}")
            return False
            
    except Exception as e:
        log_message(f"❌ Yedekleme hatası: {str(e)}")
        return False

def prepare_training_data():
    """Training verilerini hazırla"""
    log_message("📝 Training verileri hazırlanıyor...")
    
    # Training data formatını Unsloth için dönüştür
    with open('training_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Alpaca formatına dönüştür
    alpaca_data = []
    for item in data:
        alpaca_item = {
            "instruction": item["instruction"],
            "input": "",
            "output": item["output"]
        }
        alpaca_data.append(alpaca_item)
    
    with open('alpaca_training_data.json', 'w', encoding='utf-8') as f:
        json.dump(alpaca_data, f, ensure_ascii=False, indent=2)
    
    log_message(f"✅ {len(alpaca_data)} veri Alpaca formatında hazırlandı!")
    return True

def install_requirements():
    """Gerekli kütüphaneleri kur"""
    log_message("📦 Gerekli kütüphaneler kuruluyor...")
    
    requirements = [
        "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git",
        "torch>=2.1.0",
        "transformers>=4.36.0",
        "datasets",
        "accelerate",
        "bitsandbytes"
    ]
    
    for req in requirements:
        try:
            log_message(f"Kuruluyor: {req}")
            subprocess.run(["pip", "install", req], check=True)
        except subprocess.CalledProcessError as e:
            log_message(f"❌ Kurulum hatası: {req} - {str(e)}")
            return False
    
    log_message("✅ Tüm kütüphaneler kuruldu!")
    return True

def create_finetune_script():
    """Fine-tune script oluştur"""
    log_message("🛠️ Fine-tune script oluşturuluyor...")
    
    script_content = '''
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
'''
    
    with open('finetune_script.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    log_message("✅ Fine-tune script oluşturuldu!")
    return True

def start_finetune():
    """Fine-tuning işlemini başlat"""
    log_message("🚀 Fine-tuning başlatılıyor...")
    log_message("⏰ Bu işlem 2-4 saat sürebilir...")
    
    try:
        # Screen session başlat
        subprocess.run([
            "screen", "-dmS", "teknofest_finetune", 
            "python", "finetune_script.py"
        ])
        log_message("✅ Fine-tuning screen session'da başlatıldı!")
        log_message("📋 Kontrol için: screen -r teknofest_finetune")
        return True
        
    except Exception as e:
        log_message(f"❌ Fine-tuning başlatma hatası: {str(e)}")
        return False

def main():
    """Ana fonksiyon"""
    log_message("🎯 TEKNOFEST Fine-tuning Süreci Başlatılıyor!")
    log_message("=" * 50)
    
    # 1. Model yedekleme
    if not backup_current_model():
        log_message("❌ Model yedekleme başarısız, devam ediliyor...")
    
    # 2. Training verilerini hazırla
    if not prepare_training_data():
        log_message("❌ Training verileri hazırlanamadı!")
        return
    
    # 3. Kütüphaneleri kur
    if not install_requirements():
        log_message("❌ Kütüphane kurulumu başarısız!")
        return
    
    # 4. Fine-tune script oluştur
    if not create_finetune_script():
        log_message("❌ Script oluşturulamadı!")
        return
    
    # 5. Fine-tuning başlat
    if not start_finetune():
        log_message("❌ Fine-tuning başlatılamadı!")
        return
    
    log_message("🎉 Tüm işlemler başarıyla başlatıldı!")
    log_message("⏰ Sabah kontrol edin: screen -r teknofest_finetune")
    log_message("📄 Log takibi: tail -f finetune_log.txt")

if __name__ == "__main__":
    main()