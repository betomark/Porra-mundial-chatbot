import os
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from dotenv import load_dotenv
from utils.logging_config import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

class HuggingFaceLLMClient:
    """Wrapper around a HuggingFace causal LLM with 4-bit quantization support."""
    def __init__(self):
        """Initialize the HuggingFace LLM client and load the tokenizer and model."""
        logger.debug("Initializing HuggingFaceLLMClient.")
        # Use a strong 8B instruction-optimized model
        # Note: For Meta (Llama) models, you may need to accept terms on the HF website
        # A direct open alternative is "mistralai/Mistral-7B-Instruct-v0.3"
        self.model_id = os.getenv("HF_MODEL_ID", "meta-llama/Meta-Llama-3-8B-Instruct")
        
        logger.info("Loading tokenizer for %s", self.model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        
        logger.info("Loading model %s with 4-bit quantization", self.model_id)
        # Configuration to use ~5GB of RAM/VRAM instead of 16GB
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quantize_type="nf4"
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            quantization_config=quantization_config,
            device_map="auto" # Automatically distributes between GPU and CPU
        )
        logger.info("Model %s loaded successfully", self.model_id)

    def generate_prediction(self, prompt_system, prompt_user):
        """Format the chat prompt for the model and generate the prediction."""
        logger.debug("Generating prediction with HuggingFace model %s", self.model_id)
        
        # Structure the dialogue as expected by the Hugging Face model
        messages = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ]
        
        # The tokenizer converts text into tokens understandable by the model using its template
        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)
        
        # Text generation parameters
        outputs = self.model.generate(
            inputs,
            max_new_tokens=1024,   # Maximum number of tokens for the reply
            do_sample=True,         # Allow controlled creativity
            temperature=0.2,        # Low temperature for rigorous data analysis
            top_p=0.9,
            eos_token_id=self.tokenizer.eos_token_id
        )
        
        # Decode the generated tokens back to clean text
        generated_tokens = outputs[0][inputs.shape[-1]:]
        response_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        logger.info("Generated prediction with HuggingFace model %s", self.model_id)

        return response_text
