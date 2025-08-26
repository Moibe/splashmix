import random
import gradio as gr

def random_response(message, history):
    return random.choice(["Hi!", "Hello!", "Greetings!"])

with gr.Blocks() as demo:
    gr.ChatInterface(
        random_response,
        title="Greeting Bot",
        description="Ask anything and receive a nice greeting!",
    )
    gr.DeepLinkButton()

if __name__ == "__main__":
    demo.launch(share=True)