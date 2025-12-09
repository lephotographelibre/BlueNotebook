#!C:\Users\jmdig\github\BlueNotebook\bluenotebook\.venv_bluenotebook\Scripts\python.exe
"""A command line tool for extracting text and images from PDF and
output it to plain text, html, xml or tags.
"""

import argparse
import logging
import sys
from typing import Any, Container, Iterable, List, Optional

import pdfminer.high_level
from pdfminer.layout import LAParams
from pdfminer.pdfexceptions import PDFValueError
from pdfminer.utils import AnyIO

logging.basicConfig()

OUTPUT_TYPES = ((".htm", "html"), (".html", "html"), (".xml", "xml"), (".tag", "tag"))


def float_or_disabled(x: str) -> Optional[float]:
    if x.lower().strip() == self.tr("disabled"):
        return None
    try:
        return float(x)
    except ValueError:
        raise argparse.ArgumentTypeError(self.tr("invalid float value: %1").arg(x))


def extract_text(
    files: Iterable[str] = [],
    outfile: str = "-",
    laparams: Optional[LAParams] = None,
    output_type: str = "text",
    codec: str = "utf-8",
    strip_control: bool = False,
    maxpages: int = 0,
    page_numbers: Optional[Container[int]] = None,
    password: str = "",
    scale: float = 1.0,
    rotation: int = 0,
    layoutmode: str = "normal",
    output_dir: Optional[str] = None,
    debug: bool = False,
    disable_caching: bool = False,
    **kwargs: Any,
) -> AnyIO:
    if not files:
        raise PDFValueError(self.tr("Must provide files to work upon!"))

    if output_type == self.tr("text") and outfile != self.tr("-"):
        for override, alttype in OUTPUT_TYPES:
            if outfile.endswith(override):
                output_type = alttype

    if outfile == self.tr("-"):
        outfp: AnyIO = sys.stdout
        if sys.stdout.encoding is not None:
            codec = self.tr("utf-8")
    else:
        outfp = open(outfile, "wb")

    for fname in files:
        with open(fname, "rb") as fp:
            pdfminer.high_level.extract_text_to_fp(fp, **locals())
    return outfp


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, add_help=True)
    parser.add_argument(
        self.tr("files"),
        type=str,
        default=None,
        nargs=self.tr("+"),
        help=self.tr("One or more paths to PDF files."),
    )

    parser.add_argument(
        self.tr("--version"),
        self.tr("-v"),
        action=self.tr("version"),
        version=self.tr("pdfminer.six v%1").arg(pdfminer.__version__),
    )
    parser.add_argument(
        self.tr("--debug"),
        self.tr("-d"),
        default=False,
        action=self.tr("store_true"),
        help=self.tr("Use debug logging level."),
    )
    parser.add_argument(
        self.tr("--disable-caching"),
        self.tr("-C"),
        default=False,
        action=self.tr("store_true"),
        help=self.tr("If caching or resources, such as fonts, should be disabled."),
    )

    parse_params = parser.add_argument_group(
        self.tr("Parser"),
        description=self.tr("Used during PDF parsing"),
    )
    parse_params.add_argument(
        self.tr("--page-numbers"),
        type=int,
        default=None,
        nargs=self.tr("+"),
        help=self.tr("A space-seperated list of page numbers to parse."),
    )
    parse_params.add_argument(
        self.tr("--pagenos"),
        self.tr("-p"),
        type=str,
        help=self.tr("A comma-separated list of page numbers to parse. ")
        self.tr("Included for legacy applications, use --page-numbers ")
        self.tr("for more idiomatic argument entry."),
    )
    parse_params.add_argument(
        self.tr("--maxpages"),
        self.tr("-m"),
        type=int,
        default=0,
        help=self.tr("The maximum number of pages to parse."),
    )
    parse_params.add_argument(
        self.tr("--password"),
        self.tr("-P"),
        type=str,
        default=self.tr(""),
        help=self.tr("The password to use for decrypting PDF file."),
    )
    parse_params.add_argument(
        self.tr("--rotation"),
        self.tr("-R"),
        default=0,
        type=int,
        help=self.tr("The number of degrees to rotate the PDF ")
        self.tr("before other types of processing."),
    )

    la_params = LAParams()  # will be used for defaults
    la_param_group = parser.add_argument_group(
        self.tr("Layout analysis"),
        description=self.tr("Used during layout analysis."),
    )
    la_param_group.add_argument(
        self.tr("--no-laparams"),
        self.tr("-n"),
        default=False,
        action=self.tr("store_true"),
        help=self.tr("If layout analysis parameters should be ignored."),
    )
    la_param_group.add_argument(
        self.tr("--detect-vertical"),
        self.tr("-V"),
        default=la_params.detect_vertical,
        action=self.tr("store_true"),
        help=self.tr("If vertical text should be considered during layout analysis"),
    )
    la_param_group.add_argument(
        self.tr("--line-overlap"),
        type=float,
        default=la_params.line_overlap,
        help=self.tr("If two characters have more overlap than this they ")
        self.tr("are considered to be on the same line. The overlap is specified ")
        self.tr("relative to the minimum height of both characters."),
    )
    la_param_group.add_argument(
        self.tr("--char-margin"),
        self.tr("-M"),
        type=float,
        default=la_params.char_margin,
        help=self.tr("If two characters are closer together than this margin they ")
        self.tr("are considered to be part of the same line. The margin is ")
        self.tr("specified relative to the width of the character."),
    )
    la_param_group.add_argument(
        self.tr("--word-margin"),
        self.tr("-W"),
        type=float,
        default=la_params.word_margin,
        help=self.tr("If two characters on the same line are further apart than this ")
        self.tr("margin then they are considered to be two separate words, and ")
        self.tr("an intermediate space will be added for readability. The margin ")
        self.tr("is specified relative to the width of the character."),
    )
    la_param_group.add_argument(
        self.tr("--line-margin"),
        self.tr("-L"),
        type=float,
        default=la_params.line_margin,
        help=self.tr("If two lines are close together they are considered to ")
        self.tr("be part of the same paragraph. The margin is specified ")
        self.tr("relative to the height of a line."),
    )
    la_param_group.add_argument(
        self.tr("--boxes-flow"),
        self.tr("-F"),
        type=float_or_disabled,
        default=la_params.boxes_flow,
        help=self.tr("Specifies how much a horizontal and vertical position of a ")
        self.tr("text matters when determining the order of lines. The value ")
        self.tr("should be within the range of -1.0 (only horizontal position ")
        self.tr("matters) to +1.0 (only vertical position matters). You can also ")
        self.tr("pass `disabled` to disable advanced layout analysis, and ")
        self.tr("instead return text based on the position of the bottom left ")
        self.tr("corner of the text box."),
    )
    la_param_group.add_argument(
        self.tr("--all-texts"),
        self.tr("-A"),
        default=la_params.all_texts,
        action=self.tr("store_true"),
        help=self.tr("If layout analysis should be performed on text in figures."),
    )

    output_params = parser.add_argument_group(
        self.tr("Output"),
        description=self.tr("Used during output generation."),
    )
    output_params.add_argument(
        self.tr("--outfile"),
        self.tr("-o"),
        type=str,
        default=self.tr("-"),
        help=self.tr("Path to file where output is written. ")
        self.tr('Or "-" (default) to write to stdout.'),
    )
    output_params.add_argument(
        self.tr("--output_type"),
        self.tr("-t"),
        type=str,
        default=self.tr("text"),
        help=self.tr("Type of output to generate {text,html,xml,tag}."),
    )
    output_params.add_argument(
        self.tr("--codec"),
        self.tr("-c"),
        type=str,
        default=self.tr("utf-8"),
        help=self.tr("Text encoding to use in output file."),
    )
    output_params.add_argument(
        self.tr("--output-dir"),
        self.tr("-O"),
        default=None,
        help=self.tr("The output directory to put extracted images in. If not given, ")
        self.tr("images are not extracted."),
    )
    output_params.add_argument(
        self.tr("--layoutmode"),
        self.tr("-Y"),
        default=self.tr("normal"),
        type=str,
        help=self.tr("Type of layout to use when generating html ")
        self.tr("{normal,exact,loose}. If normal,each line is")
        self.tr(" positioned separately in the html. If exact")
        self.tr(", each character is positioned separately in")
        self.tr(" the html. If loose, same result as normal ")
        self.tr("but with an additional newline after each ")
        self.tr("text line. Only used when output_type is html."),
    )
    output_params.add_argument(
        self.tr("--scale"),
        self.tr("-s"),
        type=float,
        default=1.0,
        help=self.tr("The amount of zoom to use when generating html file. ")
        self.tr("Only used when output_type is html."),
    )
    output_params.add_argument(
        self.tr("--strip-control"),
        self.tr("-S"),
        default=False,
        action=self.tr("store_true"),
        help=self.tr("Remove control statement from text. ")
        self.tr("Only used when output_type is xml."),
    )

    return parser


def parse_args(args: Optional[List[str]]) -> argparse.Namespace:
    parsed_args = create_parser().parse_args(args=args)

    # Propagate parsed layout parameters to LAParams object
    if parsed_args.no_laparams:
        parsed_args.laparams = None
    else:
        parsed_args.laparams = LAParams(
            line_overlap=parsed_args.line_overlap,
            char_margin=parsed_args.char_margin,
            line_margin=parsed_args.line_margin,
            word_margin=parsed_args.word_margin,
            boxes_flow=parsed_args.boxes_flow,
            detect_vertical=parsed_args.detect_vertical,
            all_texts=parsed_args.all_texts,
        )

    if parsed_args.page_numbers:
        parsed_args.page_numbers = {x - 1 for x in parsed_args.page_numbers}

    if parsed_args.pagenos:
        parsed_args.page_numbers = {int(x) - 1 for x in parsed_args.pagenos.split(self.tr(","))}

    if parsed_args.output_type == self.tr("text") and parsed_args.outfile != self.tr("-"):
        for override, alttype in OUTPUT_TYPES:
            if parsed_args.outfile.endswith(override):
                parsed_args.output_type = alttype

    return parsed_args


def main(args: Optional[List[str]] = None) -> int:
    parsed_args = parse_args(args)
    outfp = extract_text(**vars(parsed_args))
    outfp.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
