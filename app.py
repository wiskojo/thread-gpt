import copy
import json
import os

import gradio as gr
import openai
from dotenv import load_dotenv
from gradio_pdf import PDF

from create_assistant import INSTRUCTIONS, MODEL
from thread import create_assistant_then_thread, render_markdown

load_dotenv()


OUTPUT_PATH = "data"
IMAGES_PATH = "images"


def fix_image_paths_in_thread(thread, base_path):
    for tweet in thread:
        for media in tweet.get("media"):
            media["path"] = os.path.join(
                "file", OUTPUT_PATH, os.path.basename(base_path), media["path"]
            )
    return thread


def run_create_thread(
    url_or_path, openai_api_key, assistant_instructions, assistant_model
):
    if openai_api_key is None:
        raise gr.Error("No OpenAI API Key provided.")

    client = openai.OpenAI(api_key=openai_api_key)

    try:
        saved_path = create_assistant_then_thread(
            url_or_path,
            OUTPUT_PATH,
            client,
            assistant_kwargs={
                "instructions": assistant_instructions,
                "model": assistant_model,
            },
        )
    except Exception as e:
        raise gr.Error(e)

    with open(os.path.join(saved_path, "processed_thread.json"), "r") as f:
        thread = json.load(f)

    fixed_thread = fix_image_paths_in_thread(copy.deepcopy(thread), saved_path)
    thread_md = render_markdown(fixed_thread)

    return (
        thread_md,
        json.dumps(thread, indent=2),
    )


with gr.Blocks() as demo:
    banner = gr.Markdown(
        """<div style="display: flex; align-items: center; justify-content: center; margin-top: 20px;">
      <img src="file/images/logo.png" alt="ThreadGPT Logo" style="height: 60px; margin-right: 12px; margin-top: -12px;">
      <h1 style="font-size: 48px">ThreadGPT</h1>
    </div>"""
    )

    with gr.Accordion("Configuration"):
        with gr.Row():
            api_key = gr.Textbox(
                value=os.getenv("OPENAI_API_KEY"),
                placeholder="sk-**************",
                label="OpenAI API Key",
                type="password",
                interactive=True,
            )
            with gr.Column():
                assistant_instr = gr.Textbox(
                    value=INSTRUCTIONS,
                    placeholder="Enter system instructions",
                    label="System Instructions",
                    interactive=True,
                )
                assistant_model = gr.Textbox(
                    value=MODEL,
                    placeholder="Enter model",
                    label="Model",
                    interactive=True,
                )

    with gr.Row():
        url_or_path_state = gr.State("")
        txt = gr.Textbox(
            scale=6,
            show_label=False,
            placeholder="Enter URL or local path to PDF (e.g., http://example.com/sample.pdf or /path/to/sample.pdf)",
            container=False,
        )
        btn = gr.UploadButton("Load PDF 📄", file_types=[".pdf"])

    with gr.Row(visible=False) as output_row:
        with gr.Column():
            pdf = PDF(height=900)
        with gr.Column():
            with gr.Tab("Markdown"):
                md_viewer = gr.Markdown()
            with gr.Tab("JSON"):
                json_viewer = gr.Textbox(lines=44)

    txt.submit(
        lambda url_or_path: ("", url_or_path, gr.Row(visible=True), "", ""),
        [txt],
        [txt, url_or_path_state, output_row, md_viewer, json_viewer],
    ).then(
        lambda url_or_path: url_or_path,
        [url_or_path_state],
        [pdf],
    ).then(
        run_create_thread,
        [url_or_path_state, api_key, assistant_instr, assistant_model],
        [md_viewer, json_viewer],
    )

    btn.upload(
        lambda path: (path, gr.Row(visible=True), "", ""),
        [btn],
        [url_or_path_state, output_row, md_viewer, json_viewer],
    ).then(
        lambda url_or_path: url_or_path,
        [url_or_path_state],
        [pdf],
    ).then(
        run_create_thread,
        [url_or_path_state, api_key, assistant_instr, assistant_model],
        [md_viewer, json_viewer],
    )

if __name__ == "__main__":
    demo.launch(allowed_paths=[OUTPUT_PATH, IMAGES_PATH])
