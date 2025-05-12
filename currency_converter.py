import requests
import csv
import pyttsx3
import speech_recognition as sr
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# ------------------ Text-to-Speech ------------------
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# ------------------ Speech Recognition ------------------
def get_voice_input(prompt="Say something..."):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        speak(prompt)
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio).upper()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand.")
            return ""

# ------------------ Currency Dictionary ------------------
valid_currencies = {
    "USD": "United States Dollar",
    "EUR": "Euro",
    "INR": "Indian Rupee",
    "JPY": "Japanese Yen",
    "GBP": "British Pound",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan"
}

def is_valid_currency(code):
    return code in valid_currencies

# ------------------ Converter Class ------------------
class CurrencyConverter:
    def __init__(self):
        self.history = []

    def fetch_rate(self, base, target):
        url = f"https://open.er-api.com/v6/latest/{base}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            print("API Response:", data)
        except requests.exceptions.RequestException as e:
            raise Exception("Network error or invalid API response.")

        if "rates" not in data or target not in data["rates"]:
            raise Exception(f"Invalid currency data received from API. Response: {data}")

        return data["rates"][target]





    def convert(self, amount, base, target):
        rate = self.fetch_rate(base, target)
        result = round(amount * rate, 2)
        self.history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'base': base,
            'target': target,
            'amount': amount,
            'rate': rate,
            'result': result
        })
        return result, rate

    def save_history_to_file(self, filename="conversion_history.csv"):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Base", "Target", "Amount", "Rate", "Result"])
            for record in self.history:
                writer.writerow([
                    record["timestamp"],
                    record["base"],
                    record["target"],
                    record["amount"],
                    record["rate"],
                    record["result"]
                ])
        print(f"History saved to {filename}")

# ------------------ Tkinter GUI ------------------
def run_gui():
    converter = CurrencyConverter()

    def convert():
        base = base_currency.get()
        target = target_currency.get()
        try:
            amount = float(amount_entry.get())
            if not is_valid_currency(base) or not is_valid_currency(target):
                raise ValueError("Invalid currency code.")
            result, rate = converter.convert(amount, base, target)
            result_var.set(f"{amount} {base} = {result:.2f} {target} (Rate: {rate:.2f})")
            speak(result_var.get())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_history():
        converter.save_history_to_file()
        messagebox.showinfo("Success", "History saved to CSV.")

    window = tk.Tk()
    window.title("Currency Converter")

    ttk.Label(window, text="Amount:").grid(row=0, column=0)
    amount_entry = ttk.Entry(window)
    amount_entry.grid(row=0, column=1)

    ttk.Label(window, text="From:").grid(row=1, column=0)
    base_currency = ttk.Combobox(window, values=list(valid_currencies.keys()))
    base_currency.grid(row=1, column=1)

    ttk.Label(window, text="To:").grid(row=2, column=0)
    target_currency = ttk.Combobox(window, values=list(valid_currencies.keys()))
    target_currency.grid(row=2, column=1)

    convert_button = ttk.Button(window, text="Convert", command=convert)
    convert_button.grid(row=3, column=0, columnspan=2, pady=5)

    save_button = ttk.Button(window, text="Save History", command=save_history)
    save_button.grid(row=4, column=0, columnspan=2)

    result_var = tk.StringVar()
    result_label = ttk.Label(window, textvariable=result_var, foreground="blue")
    result_label.grid(row=5, column=0, columnspan=2, pady=10)

    window.mainloop()

# ------------------ Voice Interface Option ------------------
def run_voice_interface():
    converter = CurrencyConverter()
    speak("Welcome to voice-based currency converter")

    base = get_voice_input("Say the base currency like USD or INR.")
    if not is_valid_currency(base):
        speak("Invalid currency. Exiting.")
        return

    target = get_voice_input("Say the target currency.")
    if not is_valid_currency(target):
        speak("Invalid currency. Exiting.")
        return

    try:
        amount_str = get_voice_input("Say the amount to convert.")
        amount = float(amount_str)
        result, rate = converter.convert(amount, base, target)
        message = f"{amount} {base} equals {result} {target}. Exchange rate is {rate:.2f}"
        print(message)
        speak(message)
        converter.save_history_to_file()
    except Exception as e:
        speak("Sorry, there was an error: " + str(e))

# ------------------ Main Menu ------------------
def main():
    print("=== Currency Converter ===")
    print("1. Run with GUI")
    print("2. Run with Voice Interface")
    choice = input("Choose an option (1 or 2): ")

    if choice == "1":
        run_gui()
    elif choice == "2":
        run_voice_interface()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
