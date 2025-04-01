# SVG Generation from Text Descriptions

This project implements a model that generates SVG (Scalable Vector Graphics) from text descriptions. It is designed to compete in the Kaggle "Drawing With LLMs" competition.

## Project Structure

```
svgllms/
├── kaggle_evaluation/     # Evaluation code from Kaggle
├── model.py              # Main Model class implementation
├── test_model.py         # Script to test the model locally
├── train_model.py        # Script to train the model
├── run_model.py          # Script to run the model for inference
├── models/               # Directory to store trained model parameters
├── output/               # Directory to store generated SVGs
├── requirements.txt      # Python dependencies
└── utils/                # Helper utilities
    ├── __init__.py
    ├── svg_utils.py      # SVG generation utilities
    └── text_parser.py    # Text parsing utilities
```

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r svgllms/requirements.txt
```

## Training

To train the model using the provided training data:

```bash
cd svgllms
python train_model.py
```

This will:
1. Load the training data from `train.csv`
2. Train the model for 5 epochs (configurable)
3. Save model statistics to the `models` directory

You can customize training by modifying `train_model.py` parameters:

```bash
python train_model.py --data_path /path/to/train.csv --epochs 10 --output_dir ./custom_models
```

## Running for Inference

### Interactive Mode

Run the model in interactive mode to generate SVGs from text descriptions:

```bash
cd svgllms
python run_model.py --interactive
```

Enter text descriptions when prompted, and the generated SVGs will be saved to the `output` directory.

### Batch Mode

Process a CSV file containing multiple text descriptions:

```bash
cd svgllms
python run_model.py --test /path/to/test.csv --output ./output
```

### Rendering to PNG

Add the `--render` flag to render SVGs as PNG files:

```bash
python run_model.py --interactive --render
```

## Testing the Model

Run the test script to validate the model with sample data:

```bash
cd svgllms
python test_model.py
```

This will:
1. Load test descriptions from the test.csv file
2. Generate SVGs using the model
3. Save the resulting SVGs to the output directory
4. Validate that the SVGs meet the competition constraints

## Kaggle Submission

To create a submission for the Kaggle competition:

1. Make sure your model passes the local tests
2. Push your code to a GitHub repository
3. Create a new notebook on Kaggle
4. Import your repository
5. Run the notebook to generate submissions

## Model Overview

The `Model` class in `model.py` implements the required `predict()` method for the competition. It:

1. Parses the input text description
2. Identifies key elements (colors, shapes, objects, etc.)
3. Generates an appropriate SVG representation
4. Ensures the output conforms to competition constraints

## Competition Constraints

- SVGs must be less than 10,000 bytes
- SVGs must only use allowed elements and attributes
- No external data sources or embedded images
- No CSS style elements
- SVGs must be generated within 5 minutes per description

## Future Improvements

- Enhance shape variety and complexity
- Improve semantic understanding of descriptions
- Add more refined object representations
- Implement better color combinations and patterns
- Optimize SVG size and quality
