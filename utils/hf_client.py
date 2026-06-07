import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from dotenv import load_dotenv

load_dotenv()

class HuggingFaceLLMClient:
    def __init__(self):
        # Usamos un modelo excelente de 8B parámetros optimizado para instrucciones
        # Nota: Para modelos de Meta (Llama) podrías necesitar aceptar sus términos en la web de HF
        # Una alternativa directa y libre es "mistralai/Mistral-7B-Instruct-v0.3"
        self.model_id = os.getenv("HF_MODEL_ID", "meta-llama/Meta-Llama-3-8B-Instruct")
        
        print(f"Cargando tokenizador para {self.model_id}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        
        print(f"Cargando modelo {self.model_id} con cuantización de 4 bits...")
        # Configuración para que el modelo ocupe ~5GB de RAM/VRAM en lugar de 16GB
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quantize_type="nf4"
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            quantization_config=quantization_config,
            device_map="auto" # Distribuye automáticamente entre tu Tarjeta Gráfica (GPU) y CPU
        )

    def generar_pronostico(self, prompt_sistema, prompt_usuario):
        """Aplica el formato de chat oficial del modelo y genera la predicción."""
        
        # Estructuramos el diálogo tal y como lo espera el modelo de Hugging Face
        messages = [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ]
        
        # El tokenizador convierte el texto en tokens entendibles por el modelo aplicando su plantilla
        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)
        
        # Parámetros de generación de texto
        outputs = self.model.generate(
            inputs,
            max_new_tokens=1024,   # Límite de tokens de la respuesta
            do_sample=True,         # Permitir cierta creatividad controlada
            temperature=0.2,        # Temperatura baja para análisis de datos riguroso
            top_p=0.9,
            eos_token_id=self.tokenizer.eos_token_id
        )
        
        # Decodificamos los tokens generados de vuelta a texto limpio
        generated_tokens = outputs[0][inputs.shape[-1]:]
        respuesta = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        return respuesta