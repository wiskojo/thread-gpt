<h1 style="display: flex; align-items: center; justify-content: center;">
  <img src="images/logo.png" alt="ThreadGPT Logo" style="height: 50px; margin-right: 12px; margin-top: -12px;">
  <p>ThreadGPT</p>
</h1>

Struggling to keep up with the latest AI research papers? **ThreadGPT** is here to help. It seamlessly transforms complex academic papers into concise, easy-to-understand threads. Not only does it summarize the text, but it also includes relevant figures, tables, and visuals from the papers directly into the threads. 🧵✨📄

<p align="center">
  <img src="./images/gradio.png" alt="Gradio UI" width="800">
  <br>
  <i>Gradio App UI</i>
</p>

<p align="center">
  <img src="./images/examples.png" alt="Example Threads" width="1200">
  <br>
  <i>Examples of threads generated by ThreadGPT (<a href="https://twitter.com/paper_threadoor">@paper_threadoor</a>)</i>
</p>

## 🛠️ Installation

### Clone the repo

```bash
git clone https://github.com/wiskojo/thread-gpt
```

### Install dependencies

```bash
# Install the required packages
pip install -r requirements.txt

# Install Detectron 2 for layoutparser
pip install git+https://github.com/facebookresearch/detectron2.git@v0.4
```

### Configure environment variables

Copy the `.env.template` file and fill in your `OPENAI_API_KEY`.

```bash
cp .env.template .env
```

### Create the assistant

ThreadGPT utilizes OpenAI's assistant API. To create a new assistant, run the following command:

```bash
python create_assistant.py
```

After running the command, you will receive an assistant ID. Add this ID to your `.env` file as the value for `OPENAI_ASSISTANT_ID`.

This command will create an assistant with the default prompt, name, tools, and model (`gpt-4-1106-preview`). You can customize these parameters via command-line arguments to your liking.

## 🚀 Getting Started

Before proceeding, please ensure that all the installation steps have been successfully completed.

### 🚨 Cost Warning

Please be aware that usage of GPT-4 with the assistant API can incur high costs. Make sure to monitor your usage and understand the pricing details provided by OpenAI before proceeding.

### Gradio

```bash
python app.py
```

### CLI

#### 🧵 Create Thread

To create a thread, you can either provide a URL to a file or a local path to a file. Use the following commands:

```bash
# For a URL
python thread.py <URL_TO_PDF>

# For a local file
python thread.py <LOCAL_PATH_TO_PDF>
```

By default, you will find all outputs under `./data/<PDF_NAME>`. It will have the following structure.

```
./data/<PDF_NAME>/
├── figures/
│   ├── <figure_1_name>.jpg
│   ├── <figure_2_name>.png
│   └── ...
├── <PDF_NAME>.pdf
├── results.json
├── thread.json
├── processed_thread.json
└── processed_thread.md
```

The final output for user consumption is located at `./data/<PDF_NAME>/processed_thread.md`. This file is formatted in Markdown and can be conveniently viewed using any Markdown editor.

#### All Contents
1. `figures/`: This directory contains all the figures, tables, and visuals that have been extracted from the paper.
2. `<PDF_NAME>.pdf`: This is the original PDF file.
3. `results.json`: This file contains the results of the layout parsing. It includes an index of all figures, their paths, and captions that were passed to OpenAI.
4. `thread.json`: This file contains the raw thread that was generated by OpenAI before any post-processing was done.
5. `processed_thread.json`: This file is a post-processed version of `thread.json`. The post-processing includes steps such as removing source annotations and duplicate figures.
6. `processed_thread.md`: This is a markdown version of `processed_thread.json`. It is the final output provided for user consumption.

#### 📨 Share Thread

To actually share the thread on X/Twitter, you need to set up the credentials in the `.env` file. This requires creating a [developer account](https://developer.twitter.com/) and filling in your `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_KEY`, and `ACCESS_SECRET`. Then run this command on the created JSON file:

```bash
python tweet.py ./data/<PDF_NAME>/processed_thread.json
```