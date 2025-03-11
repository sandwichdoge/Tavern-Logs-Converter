from stage1_preprocessor import LogPreprocessor
from stage2_axolotl import AxolotlConverter
import os
import argparse
from datetime import datetime


def is_st_dir(dir):
    """Check if the directory is a valid SillyTavern directory."""
    return os.path.isdir(os.path.join(dir, "public"))


def main():
    parser = argparse.ArgumentParser(description="SillyTavern log cleaner and formatter")

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Path to the SillyTavern directory",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output directory. Default: cleaned_logs",
        required=False,
        default=os.path.join(os.getcwd(), "cleaned_logs"),
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        help="Output format. Supported formats: sharegpt. Default: sharegpt",
        required=False,
        default="sharegpt",
    )
    parser.add_argument(
        "-O",
        "--obfuscate",
        type=bool,
        help="Randomize system prompt and obfuscate user names. Default: false",
        required=False,
        default=False,
    )

    args = parser.parse_args()

    # Validate input directory
    if not is_st_dir(args.input):
        print(f"Error: The provided input path: {args.input} is not a valid SillyTavern directory.")
        exit(1)

    st_dir = args.input
    output_dir = args.output
    obfuscate = args.obfuscate
    format_name = args.format

    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    stage1_out_dir = os.path.join(output_dir, "stage1_out")
    os.makedirs(stage1_out_dir, exist_ok=True)

    # Stage 1: Preprocess logs
    print(f"Stage 1: Preprocessing logs from {st_dir}...")
    processor = LogPreprocessor(st_dir, stage1_out_dir, obfuscate=obfuscate)
    logs_processed = processor.process_all_files()
    print(f"Stage 1 completed. Preprocessed {logs_processed} logs. Output saved to: {stage1_out_dir}")

    # Stage 2: Convert to specified format
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_file = os.path.join(output_dir, f"{format_name}_{timestamp}.jsonl")
    
    print(f"Stage 2: Converting to {format_name} format...")
    converter = AxolotlConverter(format_name, stage1_out_dir, final_file)
    conversations_processed = converter.process_all_files()
    print(f"Stage 2 completed. Processed {conversations_processed} conversations. Output saved to: {final_file}")


if __name__ == "__main__":
    main()