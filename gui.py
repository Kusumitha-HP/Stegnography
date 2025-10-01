import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import wave
import numpy as np

# Function to encode text within an image
def encode_text_in_image(carrier_path, secret_text):
    carrier_img = Image.open(carrier_path).convert("RGB")
    binary_text = ''.join(format(ord(char), '08b') for char in secret_text) + '00000000'  # End of text marker
    encoded_img = carrier_img.copy()
    pixels = encoded_img.load()

    data_index = 0
    for y in range(encoded_img.height):
        for x in range(encoded_img.width):
            if data_index < len(binary_text):
                r, g, b = pixels[x, y]
                # Modify the least significant bits of each color channel
                r = (r & ~1) | int(binary_text[data_index])
                if data_index + 1 < len(binary_text):
                    g = (g & ~1) | int(binary_text[data_index + 1])
                if data_index + 2 < len(binary_text):
                    b = (b & ~1) | int(binary_text[data_index + 2])

                pixels[x, y] = (r, g, b)
                data_index += 3
            else:
                break

    return encoded_img

# Function to decode text from an image
def decode_text_from_image(encoded_image_path):
    encoded_img = Image.open(encoded_image_path).convert("RGB")
    pixels = encoded_img.load()
    
    binary_text = ""
    for y in range(encoded_img.height):
        for x in range(encoded_img.width):
            r, g, b = pixels[x, y]
            binary_text += str(r & 1)
            binary_text += str(g & 1)
            binary_text += str(b & 1)

            # Check for the end of text marker
            if binary_text[-8:] == '00000000':
                binary_text = binary_text[:-8]  # Remove the end marker
                break
        else:
            continue
        break

    # Convert binary data back to text
    text = ''.join(chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8))
    return text

# Function to encode an image within another image
def encode_image_in_image(carrier_path, secret_path):
    carrier_img = Image.open(carrier_path).convert("RGB")
    secret_img = Image.open(secret_path).convert("RGB")

    # Adjust to match dimensions
    secret_img = secret_img.resize(carrier_img.size)

    encoded_img = carrier_img.copy()
    carrier_pixels = encoded_img.load()
    secret_pixels = secret_img.load()

    for y in range(secret_img.height):
        for x in range(secret_img.width):
            r_carrier, g_carrier, b_carrier = carrier_pixels[x, y]
            r_secret, g_secret, b_secret = secret_pixels[x, y]

            # Encode each RGB component of the secret image into the last two bits of the carrier image's RGB channels
            r_encoded = (r_carrier & ~3) | (r_secret >> 6)
            g_encoded = (g_carrier & ~3) | (g_secret >> 6)
            b_encoded = (b_carrier & ~3) | (b_secret >> 6)

            carrier_pixels[x, y] = (r_encoded, g_encoded, b_encoded)

    return encoded_img

# Function to decode an image from another image
def decode_image_from_image(encoded_image_path):
    encoded_img = Image.open(encoded_image_path).convert("RGB")
    decoded_img = Image.new("RGB", encoded_img.size)
    decoded_pixels = decoded_img.load()
    encoded_pixels = encoded_img.load()

    for y in range(decoded_img.height):
        for x in range(decoded_img.width):
            r_encoded, g_encoded, b_encoded = encoded_pixels[x, y]

            # Retrieve the two least significant bits and scale to full RGB values
            r_secret = (r_encoded & 3) << 6
            g_secret = (g_encoded & 3) << 6
            b_secret = (b_encoded & 3) << 6

            decoded_pixels[x, y] = (r_secret, g_secret, b_secret)

    return decoded_img

# Function to encode text within an audio file
def encode_text_in_audio(audio_path, secret_text):
    audio = wave.open(audio_path, 'rb')
    frames = audio.readframes(audio.getnframes())
    binary_text = ''.join(format(ord(char), '08b') for char in secret_text) + '00000000'  # End of text marker
    encoded_frames = bytearray(frames)

    data_index = 0
    for i in range(len(encoded_frames)):
        if data_index < len(binary_text):
            encoded_frames[i] = (encoded_frames[i] & ~1) | int(binary_text[data_index])
            data_index += 1
        else:
            break

    encoded_audio = wave.open('encoded_audio.wav', 'wb')
    encoded_audio.setparams(audio.getparams())
    encoded_audio.writeframes(bytes(encoded_frames))
    encoded_audio.close()
    audio.close()

# Function to decode text from an audio file
def decode_text_from_audio(audio_path):
    audio = wave.open(audio_path, 'rb')
    frames = audio.readframes(audio.getnframes())
    binary_text = ""

    for byte in frames:
        binary_text += str(byte & 1)

        # Check for the end of text marker
        if binary_text[-8:] == '00000000':
            binary_text = binary_text[:-8]  # Remove the end marker
            break

    audio.close()
    
    # Convert binary data back to text
    text = ''.join(chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8))
    return text

# Function to handle Video Button Click (Not implemented)
def video_not_implemented():
    messagebox.showinfo("Not Implemented", "Video encoding/decoding is yet to be implemented.")

# Initialize Tkinter GUI
root = tk.Tk()
root.title("Steganography - Text, Image, and Audio Encoding")
root.geometry("600x600")
root.configure(bg="black")

# Frame Setup
main_menu = tk.Frame(root, bg="black")
text_frame = tk.Frame(root, bg="black")
image_frame = tk.Frame(root, bg="black")
audio_frame = tk.Frame(root, bg="black")

for frame in (main_menu, text_frame, image_frame, audio_frame):
    frame.grid(row=0, column=0, sticky="nsew")

def show_frame(frame):
    frame.tkraise()

# Main Menu
tk.Label(main_menu, text="Steganography - Main Menu", font=("Arial", 16), fg="white", bg="black").pack(pady=20)

tk.Button(main_menu, text="Text", font=("Arial", 14), width=15, command=lambda: show_frame(text_frame)).pack(pady=10)
tk.Button(main_menu, text="Image", font=("Arial", 14), width=15, command=lambda: show_frame(image_frame)).pack(pady=10)
tk.Button(main_menu, text="Audio", font=("Arial", 14), width=15, command=lambda: show_frame(audio_frame)).pack(pady=10)

# Video Button that displays the "Yet to be implemented" message
tk.Button(main_menu, text="Video", font=("Arial", 14), width=15, command=video_not_implemented).pack(pady=10)

# Back Button Function
def back_to_main_menu():
    show_frame(main_menu)

# Text Frame Widgets
carrier_image_path = tk.StringVar()
text_to_encode = tk.StringVar()
encoded_image_path = tk.StringVar()

def encode_text():
    if carrier_image_path.get() and text_to_encode.get():
        encoded_img = encode_text_in_image(carrier_image_path.get(), text_to_encode.get())
        encoded_img.save("encoded_text_image.png")
        messagebox.showinfo("Success", "Text encoded successfully in encoded_text_image.png")
    else:
        messagebox.showerror("Error", "Please select a carrier image and enter text to encode.")

def decode_text():
    if encoded_image_path.get():
        decoded_text = decode_text_from_image(encoded_image_path.get())
        messagebox.showinfo("Decoded Text", f"Decoded text: {decoded_text}")
    else:
        messagebox.showerror("Error", "Please select an encoded image.")

tk.Label(text_frame, text="Carrier Image File:", font=("Arial", 12), bg="black", fg="white").pack(pady=5)
tk.Entry(text_frame, textvariable=carrier_image_path, width=40).pack(pady=5)
tk.Button(text_frame, text="Browse", command=lambda: carrier_image_path.set(filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.bmp")]))).pack(pady=5)

tk.Label(text_frame, text="Text to Encode:", font=("Arial", 12), bg="black", fg="white").pack(pady=5)
tk.Entry(text_frame, textvariable=text_to_encode, width=40).pack(pady=5)
tk.Button(text_frame, text="Encode Text", command=encode_text).pack(pady=10)

tk.Label(text_frame, text="Encoded Image File:", font=("Arial", 12), bg="black", fg="white").pack(pady=5)
tk.Entry(text_frame, textvariable=encoded_image_path, width=40).pack(pady=5)
tk.Button(text_frame, text="Browse", command=lambda: encoded_image_path.set(filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.bmp")]))).pack(pady=5)
tk.Button(text_frame, text="Decode Text", command=decode_text).pack(pady=10)

tk.Button(text_frame, text="Back", command=back_to_main_menu).pack(pady=20)

# Image Frame Widgets
carrier_image_path_img = tk.StringVar()
secret_image_path = tk.StringVar()
encoded_image_path_img = tk.StringVar()

def encode_image():
    if carrier_image_path_img.get() and secret_image_path.get():
        encoded_img = encode_image_in_image(carrier_image_path_img.get(), secret_image_path.get())
        encoded_img.save("encoded_image.png")
        messagebox.showinfo("Success", "Image encoded successfully in encoded_image.png")
    else:
        messagebox.showerror("Error", "Please select both carrier and secret images.")

def decode_image():
    if encoded_image_path_img.get():
        decoded_img = decode_image_from_image(encoded_image_path_img.get())
        decoded_img.show()
    else:
        messagebox.showerror("Error", "Please select an encoded image.")

tk.Label(image_frame, text="Carrier Image File:", font=("Arial", 12), bg="black", fg="white").pack(pady=5)
tk.Entry(image_frame, textvariable=carrier_image_path_img, width=40).pack(pady=5)
tk.Button(image_frame, text="Browse", command=lambda: carrier_image_path_img.set(filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.bmp")]))).pack(pady=5)

tk.Label(image_frame, text="Secret Image File:", font=("Arial", 12), bg="black", fg="white").pack(pady=5)
tk.Entry(image_frame, textvariable=secret_image_path, width=40).pack(pady=5)
tk.Button(image_frame, text="Browse", command=lambda: secret_image_path.set(filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.bmp")]))).pack(pady=5)
tk.Button(image_frame, text="Encode Image", command=encode_image).pack(pady=10)

tk.Label(image_frame, text="Encoded Image File:", font=("Arial", 12), bg="black", fg="white").pack(pady=5)
tk.Entry(image_frame, textvariable=encoded_image_path_img, width=40).pack(pady=5)
tk.Button(image_frame, text="Browse", command=lambda: encoded_image_path_img.set(filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.bmp")]))).pack(pady=5)
tk.Button(image_frame, text="Decode Image", command=decode_image).pack(pady=10)

tk.Button(image_frame, text="Back", command=back_to_main_menu).pack(pady=20)

# Audio Frame Widgets
audio_path = tk.StringVar()
encoded_audio_path = tk.StringVar()
text_to_encode_audio = tk.StringVar()

def encode_audio():
    if audio_path.get() and text_to_encode_audio.get():
        encode_text_in_audio(audio_path.get(), text_to_encode_audio.get())
        messagebox.showinfo("Success", "Text encoded successfully in audio.")
    else:
        messagebox.showerror("Error", "Please select an audio file and enter text to encode.")

def decode_audio():
    if encoded_audio_path.get():
        decoded_text = decode_text_from_audio(encoded_audio_path.get())
        messagebox.showinfo("Decoded Text", f"Decoded text: {decoded_text}")
    else:
        messagebox.showerror("Error", "Please select an encoded audio file.")

tk.Label(audio_frame, text="Audio File:", font=("Arial", 12), bg="black", fg="white").pack(pady=5)
tk.Entry(audio_frame, textvariable=audio_path, width=40).pack(pady=5)
tk.Button(audio_frame, text="Browse", command=lambda: audio_path.set(filedialog.askopenfilename(filetypes=[("Audio files", "*.wav")]))).pack(pady=5)

tk.Label(audio_frame, text="Text to Encode:", font=("Arial", 12), bg="black", fg="white").pack(pady=5)
tk.Entry(audio_frame, textvariable=text_to_encode_audio, width=40).pack(pady=5)
tk.Button(audio_frame, text="Encode Text", command=encode_audio).pack(pady=10)

tk.Label(audio_frame, text="Encoded Audio File:", font=("Arial", 12), bg="black", fg="white").pack(pady=5)
tk.Entry(audio_frame, textvariable=encoded_audio_path, width=40).pack(pady=5)
tk.Button(audio_frame, text="Browse", command=lambda: encoded_audio_path.set(filedialog.askopenfilename(filetypes=[("Audio files", "*.wav")]))).pack(pady=5)
tk.Button(audio_frame, text="Decode Audio", command=decode_audio).pack(pady=10)

tk.Button(audio_frame, text="Back", command=back_to_main_menu).pack(pady=20)

# Show the main menu frame
show_frame(main_menu)

# Run the Tkinter event loop
root.mainloop()
