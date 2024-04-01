import clean_st_jsonl_logs
import os
import argparse


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

    logs_processed = clean_st_jsonl_logs.execute(st_dir, output_dir)
    print("Stage 1 done. Total {} logs. Output saved to: {}".format(logs_processed, output_dir))


if __name__ == "__main__":
    main()
