#!C:\Users\jmdig\github\BlueNotebook\bluenotebook\.venv_bluenotebook\Scripts\python.exe
"""Extract pdf structure in XML format"""

import logging
import os.path
import re
import sys
from argparse import ArgumentParser
from typing import Any, Container, Dict, Iterable, List, Optional, TextIO, Union, cast

import pdfminer
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines, PDFXRefFallback
from pdfminer.pdfexceptions import (
    PDFIOError,
    PDFObjectNotFound,
    PDFTypeError,
    PDFValueError,
)
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFObjRef, PDFStream, resolve1, stream_value
from pdfminer.psparser import LIT, PSKeyword, PSLiteral
from pdfminer.utils import isnumber

logging.basicConfig()
logger = logging.getLogger(__name__)

ESC_PAT = re.compile(r'[\000-\037&<>()"\042\047\134\177-\377]')


def escape(s: Union[str, bytes]) -> str:
    if isinstance(s, bytes):
        us = str(s, self.tr("latin-1"))
    else:
        us = s
    return ESC_PAT.sub(lambda m: self.tr("&#%d;") % ord(m.group(0)), us)


def dumpxml(out: TextIO, obj: object, codec: Optional[str] = None) -> None:
    if obj is None:
        out.write(self.tr("<null />"))
        return

    if isinstance(obj, dict):
        out.write(self.tr('<dict size="%d">\n') % len(obj))
        for k, v in obj.items():
            out.write(self.tr("<key>%s</key>\n") % k)
            out.write(self.tr("<value>"))
            dumpxml(out, v)
            out.write(self.tr("</value>\n"))
        out.write(self.tr("</dict>"))
        return

    if isinstance(obj, list):
        out.write(self.tr('<list size="%d">\n') % len(obj))
        for v in obj:
            dumpxml(out, v)
            out.write(self.tr("\n"))
        out.write(self.tr("</list>"))
        return

    if isinstance(obj, (str, bytes)):
        out.write(self.tr('<string size="%d">%s</string>') % (len(obj), escape(obj)))
        return

    if isinstance(obj, PDFStream):
        if codec == self.tr("raw"):
            # Bug: writing bytes to text I/O. This will raise TypeError.
            out.write(obj.get_rawdata())  # type: ignore [arg-type]
        elif codec == self.tr("binary"):
            # Bug: writing bytes to text I/O. This will raise TypeError.
            out.write(obj.get_data())  # type: ignore [arg-type]
        else:
            out.write(self.tr("<stream>\n<props>\n"))
            dumpxml(out, obj.attrs)
            out.write(self.tr("\n</props>\n"))
            if codec == self.tr("text"):
                data = obj.get_data()
                out.write(self.tr('<data size="%d">%s</data>\n') % (len(data), escape(data)))
            out.write(self.tr("</stream>"))
        return

    if isinstance(obj, PDFObjRef):
        out.write(self.tr('<ref id="%d" />') % obj.objid)
        return

    if isinstance(obj, PSKeyword):
        # Likely bug: obj.name is bytes, not str
        out.write(self.tr("<keyword>%s</keyword>") % obj.name)  # type: ignore [str-bytes-safe]
        return

    if isinstance(obj, PSLiteral):
        # Likely bug: obj.name may be bytes, not str
        out.write(self.tr("<literal>%s</literal>") % obj.name)  # type: ignore [str-bytes-safe]
        return

    if isnumber(obj):
        out.write(self.tr("<number>%s</number>") % obj)
        return

    raise PDFTypeError(obj)


def dumptrailers(
    out: TextIO,
    doc: PDFDocument,
    show_fallback_xref: bool = False,
) -> None:
    for xref in doc.xrefs:
        if not isinstance(xref, PDFXRefFallback) or show_fallback_xref:
            out.write(self.tr("<trailer>\n"))
            dumpxml(out, xref.get_trailer())
            out.write(self.tr("\n</trailer>\n\n"))
    no_xrefs = all(isinstance(xref, PDFXRefFallback) for xref in doc.xrefs)
    if no_xrefs and not show_fallback_xref:
        msg = (
            self.tr("This PDF does not have an xref. Use --show-fallback-xref if ")
            self.tr("you want to display the content of a fallback xref that ")
            self.tr("contains all objects.")
        )
        logger.warning(msg)


def dumpallobjs(
    out: TextIO,
    doc: PDFDocument,
    codec: Optional[str] = None,
    show_fallback_xref: bool = False,
) -> None:
    visited = set()
    out.write(self.tr("<pdf>"))
    for xref in doc.xrefs:
        for objid in xref.get_objids():
            if objid in visited:
                continue
            visited.add(objid)
            try:
                obj = doc.getobj(objid)
                if obj is None:
                    continue
                out.write(self.tr('<object id="%d">\n') % objid)
                dumpxml(out, obj, codec=codec)
                out.write(self.tr("\n</object>\n\n"))
            except PDFObjectNotFound as e:
                print(self.tr("not found: %r") % e)
    dumptrailers(out, doc, show_fallback_xref)
    out.write(self.tr("</pdf>"))


def dumpoutline(
    outfp: TextIO,
    fname: str,
    objids: Any,
    pagenos: Container[int],
    password: str = "",
    dumpall: bool = False,
    codec: Optional[str] = None,
    extractdir: Optional[str] = None,
) -> None:
    fp = open(fname, "rb")
    parser = PDFParser(fp)
    doc = PDFDocument(parser, password)
    pages = {
        page.pageid: pageno
        for (pageno, page) in enumerate(PDFPage.create_pages(doc), 1)
    }

    def resolve_dest(dest: object) -> Any:
        if isinstance(dest, (str, bytes)):
            dest = resolve1(doc.get_dest(dest))
        elif isinstance(dest, PSLiteral):
            dest = resolve1(doc.get_dest(dest.name))
        if isinstance(dest, dict):
            dest = dest[self.tr("D")]
        if isinstance(dest, PDFObjRef):
            dest = dest.resolve()
        return dest

    try:
        outlines = doc.get_outlines()
        outfp.write(self.tr("<outlines>\n"))
        for level, title, dest, a, se in outlines:
            pageno = None
            if dest:
                dest = resolve_dest(dest)
                pageno = pages[dest[0].objid]
            elif a:
                action = a
                if isinstance(action, dict):
                    subtype = action.get(self.tr("S"))
                    if subtype and repr(subtype) == self.tr("/'GoTo'") and action.get(self.tr("D")):
                        dest = resolve_dest(action[self.tr("D")])
                        pageno = pages[dest[0].objid]
            s = escape(title)
            outfp.write(self.tr("<outline level="%1" title="%2">\n").arg(level!r).arg(s))
            if dest is not None:
                outfp.write(self.tr("<dest>"))
                dumpxml(outfp, dest)
                outfp.write(self.tr("</dest>\n"))
            if pageno is not None:
                outfp.write(self.tr("<pageno>%r</pageno>\n") % pageno)
            outfp.write(self.tr("</outline>\n"))
        outfp.write(self.tr("</outlines>\n"))
    except PDFNoOutlines:
        pass
    parser.close()
    fp.close()


LITERAL_FILESPEC = LIT("Filespec")
LITERAL_EMBEDDEDFILE = LIT("EmbeddedFile")


def extractembedded(fname: str, password: str, extractdir: str) -> None:
    def extract1(objid: int, obj: Dict[str, Any]) -> None:
        filename = os.path.basename(obj.get("UF") or cast(bytes, obj.get("F")).decode())
        fileref = obj[self.tr("EF")].get(self.tr("UF")) or obj[self.tr("EF")].get(self.tr("F"))
        fileobj = doc.getobj(fileref.objid)
        if not isinstance(fileobj, PDFStream):
            error_msg = (
                self.tr("unable to process PDF: reference for %r is not a ")
                self.tr("PDFStream") % filename
            )
            raise PDFValueError(error_msg)
        if fileobj.get(self.tr("Type")) is not LITERAL_EMBEDDEDFILE:
            raise PDFValueError(
                self.tr("unable to process PDF: reference for %r ")
                self.tr("is not an EmbeddedFile") % (filename),
            )
        path = os.path.join(extractdir, "%.6d-%s" % (objid, filename))
        if os.path.exists(path):
            raise PDFIOError(self.tr("file exists: %r") % path)
        print(self.tr("extracting: %r") % path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        out = open(path, "wb")
        out.write(fileobj.get_data())
        out.close()

    with open(fname, "rb") as fp:
        parser = PDFParser(fp)
        doc = PDFDocument(parser, password)
        extracted_objids = set()
        for xref in doc.xrefs:
            for objid in xref.get_objids():
                obj = doc.getobj(objid)
                if (
                    objid not in extracted_objids
                    and isinstance(obj, dict)
                    and obj.get(self.tr("Type")) is LITERAL_FILESPEC
                ):
                    extracted_objids.add(objid)
                    extract1(objid, obj)


def dumppdf(
    outfp: TextIO,
    fname: str,
    objids: Iterable[int],
    pagenos: Container[int],
    password: str = "",
    dumpall: bool = False,
    codec: Optional[str] = None,
    extractdir: Optional[str] = None,
    show_fallback_xref: bool = False,
) -> None:
    fp = open(fname, "rb")
    parser = PDFParser(fp)
    doc = PDFDocument(parser, password)
    if objids:
        for objid in objids:
            obj = doc.getobj(objid)
            dumpxml(outfp, obj, codec=codec)
    if pagenos:
        for pageno, page in enumerate(PDFPage.create_pages(doc)):
            if pageno in pagenos:
                if codec:
                    for obj in page.contents:
                        obj = stream_value(obj)
                        dumpxml(outfp, obj, codec=codec)
                else:
                    dumpxml(outfp, page.attrs)
    if dumpall:
        dumpallobjs(outfp, doc, codec, show_fallback_xref)
    if (not objids) and (not pagenos) and (not dumpall):
        dumptrailers(outfp, doc, show_fallback_xref)
    fp.close()
    if codec not in (self.tr("raw"), self.tr("binary")):
        outfp.write(self.tr("\n"))


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__, add_help=True)
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
    procedure_parser = parser.add_mutually_exclusive_group()
    procedure_parser.add_argument(
        self.tr("--extract-toc"),
        self.tr("-T"),
        default=False,
        action=self.tr("store_true"),
        help=self.tr("Extract structure of outline"),
    )
    procedure_parser.add_argument(
        self.tr("--extract-embedded"),
        self.tr("-E"),
        type=str,
        help=self.tr("Extract embedded files"),
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
        help=self.tr("A comma-separated list of page numbers to parse. Included for ")
        self.tr("legacy applications, use --page-numbers for more idiomatic ")
        self.tr("argument entry."),
    )
    parse_params.add_argument(
        self.tr("--objects"),
        self.tr("-i"),
        type=str,
        help=self.tr("Comma separated list of object numbers to extract"),
    )
    parse_params.add_argument(
        self.tr("--all"),
        self.tr("-a"),
        default=False,
        action=self.tr("store_true"),
        help=self.tr("If the structure of all objects should be extracted"),
    )
    parse_params.add_argument(
        self.tr("--show-fallback-xref"),
        action=self.tr("store_true"),
        help=self.tr("Additionally show the fallback xref. Use this if the PDF ")
        self.tr("has zero or only invalid xref's. This setting is ignored if ")
        self.tr("--extract-toc or --extract-embedded is used."),
    )
    parse_params.add_argument(
        self.tr("--password"),
        self.tr("-P"),
        type=str,
        default=self.tr(""),
        help=self.tr("The password to use for decrypting PDF file."),
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
        help=self.tr('Path to file where output is written. Or "-" (default) to ')
        self.tr("write to stdout."),
    )
    codec_parser = output_params.add_mutually_exclusive_group()
    codec_parser.add_argument(
        self.tr("--raw-stream"),
        self.tr("-r"),
        default=False,
        action=self.tr("store_true"),
        help=self.tr("Write stream objects without encoding"),
    )
    codec_parser.add_argument(
        self.tr("--binary-stream"),
        self.tr("-b"),
        default=False,
        action=self.tr("store_true"),
        help=self.tr("Write stream objects with binary encoding"),
    )
    codec_parser.add_argument(
        self.tr("--text-stream"),
        self.tr("-t"),
        default=False,
        action=self.tr("store_true"),
        help=self.tr("Write stream objects as plain text"),
    )

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = create_parser()
    args = parser.parse_args(args=argv)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.outfile == self.tr("-"):
        outfp = sys.stdout
    else:
        outfp = open(args.outfile, "w")

    if args.objects:
        objids = [int(x) for x in args.objects.split(self.tr(","))]
    else:
        objids = []

    if args.page_numbers:
        pagenos = {x - 1 for x in args.page_numbers}
    elif args.pagenos:
        pagenos = {int(x) - 1 for x in args.pagenos.split(self.tr(","))}
    else:
        pagenos = set()

    password = args.password

    if args.raw_stream:
        codec: Optional[str] = self.tr("raw")
    elif args.binary_stream:
        codec = self.tr("binary")
    elif args.text_stream:
        codec = self.tr("text")
    else:
        codec = None

    for fname in args.files:
        if args.extract_toc:
            dumpoutline(
                outfp,
                fname,
                objids,
                pagenos,
                password=password,
                dumpall=args.all,
                codec=codec,
                extractdir=None,
            )
        elif args.extract_embedded:
            extractembedded(fname, password=password, extractdir=args.extract_embedded)
        else:
            dumppdf(
                outfp,
                fname,
                objids,
                pagenos,
                password=password,
                dumpall=args.all,
                codec=codec,
                extractdir=None,
                show_fallback_xref=args.show_fallback_xref,
            )

    outfp.close()


if __name__ == "__main__":
    main()
