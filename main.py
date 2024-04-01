import stage1_preprocessor
import stage2_axolotl
import os
import argparse
from datetime import datetime


def is_st_dir(dir):
    return os.path.isdir(dir + "/public")


def main():
    parser = argparse.ArgumentParser(description="cleaner")

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
    )

    args = parser.parse_args()

    if not is_st_dir(args.input):
        print(f"The provided input path: {args.input} is not a valid SillyTavern directory.")
        exit()

    st_dir = args.input
    output_dir = args.output

    if not args.output:
        output_dir = os.getcwd() + "/cleaned_logs"

    stage1_out_dir = output_dir + "/stage1_out"

    logs_processed = stage1_preprocessor.execute(st_dir, stage1_out_dir)
    print("Stage 1 done. Preprocessed {} logs in total. Output saved to: {}".format(logs_processed, stage1_out_dir))

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_file = output_dir + "/sharegpt_" + timestamp + ".jsonl"

    stage2_axolotl.to_format("sharegpt", stage1_out_dir, final_file)
    print("Stage 2 done. Output saved to: {}".format(final_file))


if __name__ == "__main__":
    main()
