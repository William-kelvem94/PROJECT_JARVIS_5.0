"""Local neural brain for Jarvis.

This component maintains its own small language model (based on GPT-2/distilgpt2)
that can be fine-tuned on the agent's interaction history. The Ollama model is
used as an assistant/fallback when the local brain is missing or uncertain.

API:
    brain = LocalBrain()
    resp = brain.reply(user_text, history_prompt)
    brain.train_from_file("data/interactions.jsonl")

Model storage: `jarvis_minimal/models/local_brain/` (HuggingFace format).
"""
import os
import json
import logging
from typing import List, Optional


logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "local_brain")
BASE_MODEL = "distilgpt2"  # small model to start


class LocalBrain:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            if os.path.isdir(MODEL_DIR) and os.listdir(MODEL_DIR):
                self.tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
                self.model = AutoModelForCausalLM.from_pretrained(MODEL_DIR)
                logger.info("LocalBrain: modelo carregado de %s", MODEL_DIR)
            else:
                # initialize base model and tokenizer (not trained)
                self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
                self.model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)
                logger.info("LocalBrain: usando base model %s (não treinado)", BASE_MODEL)
        except Exception as e:
            logger.warning("LocalBrain: falha ao carregar modelo - %s", e)
            self.model = None
            self.tokenizer = None

    def reply(self, user_text: str, history_prompt: str = "") -> Optional[str]:
        """Generate a response using the local model. Returns None/empty if not available."""
        if self.model is None or self.tokenizer is None:
            return None
        try:
            # build prompt and ensure it won't exceed the model's maximum
            prompt = history_prompt + "\nUsuário: " + user_text + "\nJarvis:" if history_prompt else user_text
            # the model has a fixed context size; reserve some room for the
            # generated tokens (max_new_tokens).  If the prompt is too long, the
            # tokenizer with ``truncation=True`` will drop tokens from the left.
            max_ctx = getattr(self.tokenizer, "model_max_length", None)
            if max_ctx is None:
                max_ctx = 1024
            # leave space for new tokens
            prompt_enc = self.tokenizer(prompt, return_tensors="pt", truncation=True,
                                        max_length=max_ctx - 150)
            outputs = self.model.generate(**prompt_enc, max_new_tokens=150,
                                          pad_token_id=self.tokenizer.eos_token_id)
            text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # cut off prompt portion robustly
            if "Jarvis:" in text:
                text = text.split("Jarvis:")[-1].strip()
            # fallback if split failed or model echoed system prompt
            if "Você é Jarvis" in text:
                text = text.split(user_text)[-1].strip() if user_text in text else text
            return text
        except Exception as e:
            logger.error("LocalBrain.reply error: %s", e)
            return None

    def train_from_file(self, path: str = "data/interactions.jsonl", epochs: int = 1, learning_rate: float = 5e-5, batch_size: int = 1):
        """Fine-tune the local model with advanced parameters."""
        try:
            from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling, AutoTokenizer, AutoModelForCausalLM
            from datasets import load_dataset
        except ImportError:
            logger.error("LocalBrain training requires transformers and datasets packages.")
            return

        if not os.path.isfile(path):
            logger.warning("LocalBrain: arquivo de interações não encontrado: %s", path)
            return

        # build dataset: each line {"user":.., "assistant":..}
        examples = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    j = json.loads(line)
                    usr = j.get("user", "")
                    ast = j.get("assistant", "")
                    if usr and ast:
                        examples.append("Usuário: " + usr + "\nJarvis: " + ast)
                except Exception:
                    continue
        if not examples:
            logger.warning("LocalBrain: nenhuma interação válida para treinar")
            return

        ds = load_dataset("text", data_files={"train": path})
        tokenizer = self.tokenizer or AutoTokenizer.from_pretrained(BASE_MODEL)
        model = self.model or AutoModelForCausalLM.from_pretrained(BASE_MODEL)

        def tokenize_function(examples):
            return tokenizer(examples["text"], truncation=True, max_length=512)

        tokenized = ds.map(tokenize_function, batched=True, remove_columns=["text"])
        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
        from transformers import TrainerCallback
        class DashboardCallback(TrainerCallback):
            def on_log(self, args, state, control, logs=None, **kwargs):
                if logs and "loss" in logs:
                    from .dashboard_server import log_task
                    loss = logs["loss"]
                    epoch = logs.get("epoch", 0)
                    step = state.global_step
                    log_task(f"📉 Treino: Passo {step} | Época {epoch:.2f} | Loss: {loss:.4f}")

        training_args = TrainingArguments(
            output_dir=MODEL_DIR,
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=0.01,
            save_steps=1000,
            save_total_limit=1,
            logging_steps=1, 
        )
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized["train"],
            data_collator=data_collator,
            callbacks=[DashboardCallback()]
        )
        history = trainer.train()
        trainer.save_model(MODEL_DIR)
        self.model = model
        self.tokenizer = tokenizer
        logger.info("LocalBrain: treinamento concluído e modelo salvo em %s", MODEL_DIR)
        # save loss history to file for later inspection
        try:
            logs = []
            for entry in trainer.state.log_history:
                # only keep loss/epoch info
                rec = {}
                for k in ("loss", "epoch", "step"): 
                    if k in entry:
                        rec[k] = entry[k]
                if rec:
                    logs.append(rec)
            if logs:
                import json
                with open(os.path.join(MODEL_DIR, "training_log.json"), "w", encoding="utf-8") as f:
                    json.dump(logs, f, indent=2)
        except Exception:
            pass
        return {"examples": len(examples), "log_history": logs if 'logs' in locals() else []}
