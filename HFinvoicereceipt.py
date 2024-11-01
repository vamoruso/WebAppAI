import torch
import re
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel


device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
processor = DonutProcessor.from_pretrained("AdamCodd/donut-receipts-extract")
model = VisionEncoderDecoderModel.from_pretrained("AdamCodd/donut-receipts-extract")
model.to(device)

def load_and_preprocess_image(image_path: str, processor):
    """
    Carica un'immagine e preelaborala per il modello.
    """
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(image, return_tensors="pt").pixel_values
    return pixel_values

def generate_text_from_image(model, image_path: str, processor, device):
    """
    Genera testo da un'immagine utilizzando il modello addestrato.
    """
    # Carica e processa l’ immagine
    pixel_values = load_and_preprocess_image(image_path, processor)
    pixel_values = pixel_values.to(device)

    # Genera output utilizzando il modello
    model.eval()
    with torch.no_grad():
        task_prompt = "<s_cord-v2>"
        decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False,
                                                return_tensors="pt").input_ids
        decoder_input_ids = decoder_input_ids.to(device)
        generated_outputs = model.generate(
            pixel_values,
            decoder_input_ids=decoder_input_ids,
            max_length=model.decoder.config.max_position_embeddings,
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
            early_stopping=True,
            bad_words_ids=[[processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True
        )

    # Decodifica l'output generato
    decoded_text = processor.batch_decode(generated_outputs.sequences)[0]
    decoded_text = decoded_text.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token,
                                                                                   "")
    decoded_text = re.sub(r"<.*?>", "", decoded_text, count=1).strip()  # rimuove il primo token di inizio
    decoded_text = processor.token2json(decoded_text)
    return decoded_text

def readInfo( image_path):
    """
       Analizza il contenuto dell'immagine.
    """
    extracted_text = generate_text_from_image(model, image_path, processor, device)
    return extracted_text

def unitTest():
    image_path = r"D:\tess4j\imagedataset\1197-receipt.jpg"  # Replace with your image path
    extracted_text = readInfo(image_path)
    print("Extracted Text:", extracted_text)

if __name__ == '__main__':
    unitTest()