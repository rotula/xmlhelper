#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
XML helper: bundles commonly used functions for text processing
with lxml
"""

try:
    from builtins import str as unitext  # python 2/3
except ImportError:  # pragma: no cover
    unitext = unicode
from copy import deepcopy
from doctest import Example
import unittest

from lxml import etree as et
from lxml.doctestcompare import LXMLOutputChecker

__version__ = "0.22.3"
__author__ = "Clemens Radl <clemens.radl@googlemail.com>"

TEXT = 1
TAIL = 2

# A dictionary of commonly used namespaces.

# @@@TODO: a more complete list
# @@@TODO: check, how to handle slashes and hashes
#          maybe make two lists, one for XML and one
#          for RDF

ns = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "dbpedia": "http://dbpedia.org/resource/",
    "dbpedia-owl": "http://dbpedia.org/ontology/",
    "dbpprop": "http://dbpedia.org/property/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcam": "http://purl.org/dc/dcam/",
    "dcterms": "http://purl.org/dc/terms/",
    "dctype": "http://purl.org/dc/dcmitype/",
    "dmgh": "http://www.mgh.de/ns/dmgh/",
    "docxm": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "dv": "http://dfg-viewer.de/",
    "exif": "http://www.w3.org/2003/12/exif/ns",
    "fo": "http://www.w3.org/1999/XSL/Format",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "frbr": "http://purl.org/vocab/frbr/core#",
    "ftr": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer",
    "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "geonames": "http://www.geonames.org/ontology#",
    "georss": "http://www.georss.org/georss",
    "geosparql": "http://www.opengis.net/ont/geosparql#",
    "gml": "http://www.opengis.net/gml",
    "gndo": "http://d-nb.info/standards/elementset/gnd#",
    "hdr": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header",
    "html": "http://www.w3.org/1999/xhtml",
    "ical": "http://www.w3.org/2002/12/cal/ical#",
    "kml": "http://www.opengis.net/kml/2.2",
    "m": "http://www.w3.org/1998/Math/MathML",
    "marc": "http://www.loc.gov/MARC21/slim",
    "mets": "http://www.loc.gov/METS/",
    "mgh": "http://www.mgh.de/ns/mgh/",
    "mix": "http://www.loc.gov/mix/v10",
    "mods": "http://www.loc.gov/mods/v3",
    "o": "urn:schemas-microsoft-com:office:office",
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
    "openSearch": "http://a9.com/-/spec/opensearchrss/1.0/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "packrel":  "http://schemas.openxmlformats.org/package/2006/relationships",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfa": "http://www.w3.org/ns/rdfa#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rss": "http://purl.org/rss/1.0/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "svg": "http://www.w3.org/2000/svg",
    "tei": "http://www.tei-c.org/ns/1.0",
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "v": "urn:schemas-microsoft-com:vml",
    "ve": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w10": "urn:schemas-microsoft-com:office:word",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "wot": "http://xmlns.com/wot/0.1/",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "xlink": "http://www.w3.org/1999/xlink",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "xs": "http://www.w3.org/2001/XMLSchema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xsl": "http://www.w3.org/1999/XSL/Transform",
}

class XMLHelperError(Exception):
    """Exception"""

class FollowingIterator(object):
    """
    Iterator that yields all elements (not comments etc.) of the following axis

    Hopefully, this is somewhat faster than repeatedly calling the
    equivalent xpaths.
    """

    def __init__(self, element):
        """
        Initialize iterator
        """
        self.start_element = element
        self.current_element = element
        self.b_done = False

    def __iter__(self):
        """
        Return the iterator (self)
        """
        return self

    def __next__(self):
        return self.next()  # pragma: no cover

    def next(self):
        """
        Advance one step or raise exception.
        """
        if self.b_done:
            raise StopIteration
        if self.current_element == self.start_element or \
                len(self.current_element) == 0:
            ret = self.current_element.getnext()
            parent = self.current_element
            while ret is None:
                parent = parent.getparent()
                if parent is None:
                    self.b_done = True
                    raise StopIteration
                ret = parent.getnext()
            self.current_element = ret
            return ret
        else:
            self.current_element = self.current_element[0]
            return self.current_element

class PrecedingIterator(object):
    """
    Iterator that yields all elements (not comments etc.) of the preceding axis

    Hopefully, this is somewhat faster than repeatedly calling the
    equivalent xpaths.
    """
    
    def __init__(self, element):
        """
        Initialize iterator
        """
        self.start_element = element
        self.current_element = element
        self.b_done = False
        # establish list of ancestors
        self.ancestors = []
        ancestor = element.getparent()
        while ancestor is not None:
            self.ancestors.append(ancestor)
            ancestor = ancestor.getparent()
        if len(self.ancestors) == 0:
            # We initialized with the root element.
            self.b_done = True

    def __iter__(self):
        """
        Return the iterator (self)
        """
        return self

    def __next__(self):
        return self.next()  # pragma: no cover

    def next(self):
        """
        Advance one step or raise exception
        """
        if self.b_done:
            raise StopIteration
        prv = self.current_element.getprevious()
        if prv is not None:
            # dive into the element
            if len(prv) == 0:
                self.current_element = prv
                return prv
            while len(prv) > 0:
                prv = prv[-1]
            self.current_element = prv
            return prv
        else:
            # no previous element found
            parent = self.current_element.getparent()
            if parent is None:
                self.b_done = True
                raise StopIteration
            if parent not in self.ancestors:
                self.current_element = parent
                return parent
            else:
                # We may not use this element,
                # as it is in the ancestors list,
                # but we just set it as the current
                # element and move on without returning
                # anything.
                self.current_element = parent
                return self.next()

class AllChildNodesIterator(object):
    """Iterator over all children of an element (including TextNodes)"""

    current_node = None
    b_text_sent = False

    def __init__(self, element):
        """Initialize"""
        self.element = element
        self.current_node = TextNode(element.text, element)

    def __iter__(self):
        """Return the iterator (self)"""
        return self
    
    def __next__(self):
        return self.next()  # pragma: no cover

    def next(self):
        if self.current_node is None:
            raise StopIteration
        ret = self.current_node
        if isinstance(self.current_node, TextNode):
            self.current_node = self.current_node.getnext()
        else:
            self.current_node = TextNode(
                self.current_node.tail, self.element, self.current_node)
        return ret

class FollowingNodesIterator(object):
    """Iterator over all following nodes (including TextNodes)"""

    b_done = False
    start_node = None
    current_node = None

    def __init__(self, node):
        self.start_node = node
        self.current_node = node

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()  # pragma: no cover

    def _getnext(self, e):
        if isinstance(e, TextNode):
            return e.getnext()
        if e.getparent() is not None:
            return TextNode(e.tail, e.getparent(), e)
        return None

    def next(self):
        if self.b_done:
            raise StopIteration
        if (self.current_node == self.start_node
                or isinstance(self.current_node, TextNode)):
            ret = self._getnext(self.current_node)
            parent = self.current_node
            while ret is None:
                parent = parent.getparent()
                if parent is None:
                    self.b_done = True
                    raise StopIteration
                ret = self._getnext(parent)
            self.current_node = ret
            return ret
        else:
            ret = TextNode(
                self.current_node.text,
                self.current_node
            )
            self.current_node = ret
            return self.current_node

class TextNode(object):
    """A simple node type to represent text that "knows"
    about its position in the document
    """

    text = ""
    parent = None
    # the element this is a tail of,
    # if None, then it's text of the parent
    previous = None
    # if text node is empty
    empty = False

    def __init__(self, text, parent, previous=None):
        """Initialize"""
        if text is None:
            self.text = ""
            self.empty = True
        else:
            self.text = text
        self.parent = parent
        self.previous = previous

    def getparent(self):
        return self.parent
    
    def getprevious(self):
        return self.previous

    def getnext(self):
        if self.previous is None:
            if len(self.parent):
                return self.parent[0]
            return None
        return self.previous.getnext()

    def tag(self):
        return TextNode

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        return (self.text == other.text
                and self.parent == other.parent
                and self.previous == other.previous)
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return (self.text, self.parent, self.previous).__hash__()

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        return u"TextNode('{}')".format(self.text)

    def __str__(self):
        return self.text

class TransformerError(XMLHelperError):
    pass

class TransformerNotFoundError(TransformerError):
    pass

class Transformer(object):
    """Basic infrastructure for a simple XML transformer
    """

    # the input ElementTree
    input_doc = None
    # the root Element
    root = None
    # dictionary for index
    _ids = None
    # skip processing instructions?
    skip_pis = False
    # skip comments?
    skip_comments = False
    # stack of nodes in front of the root element
    front_nodes = None
    # strip namespaces
    strip_namespaces = False
    # nodes to skip in ordinary processing,
    # as they are used elsewhere or to be
    # ignored completely
    skip_nodes = None

    def __init__(self, input_doc, **kwargs):
        if isinstance(input_doc, et._Element):
            self.input_doc = et.ElementTree(input_doc)
            self.root = input_doc
        elif isinstance(input_doc, et._ElementTree):
            self.input_doc = input_doc
            self.root = input_doc.getroot()
        self._ids = {}
        self.front_nodes = self._get_front_nodes()
        self.skip_nodes = set()
        for (k, v) in kwargs.items():
            if k == "skip_pis":
                self.skip_pis = v
            elif k == "skip_comments":
                self.skip_comments = v
            elif k == "strip_namespaces":
                self.strip_namespaces = v

    def __repr__(self):
        return u"Transformer({})".format(self.input_doc)

    def __str__(self):
        return self.__repr__()

    def _get_front_nodes(self):
        """Return list of nodes in front of the root node
        in document order.
        """
        ret = []
        node = self.root.getprevious()
        while node is not None:
            ret.append(node)
            node = node.getprevious()
        return ret

    def transform(self):
        """Run the transformation"""
        self._preprocessing()
        self.index()
        ret = self._transform_document()
        ret = self._post_processing(ret)
        try:
            return et.ElementTree(ret)
        except:
            # treat ret as a list
            output = []
            for e in ret:
                if isinstance(e, (str, unitext)):
                    output.append(e)
                else:
                    try:
                        output.append(et.tostring(e, encoding="unicode"))
                    except:
                        output.append(unitext(e))
            return u"".join(output)

    def _preprocessing(self):
        """"Hook for any preliminary processing needed."""
        return

    def index_iter(self):
        """Iterate over all elements, add them to the default index.
        """
        for e in self.root.iter():
            self._add_to_id_index(e)
            yield e

    def index(self):
        """Build indexes, should be overridden

        The default is to collect all xml:ids to be able
        to implement get_element_by_id().

        If you override the indexing method (which you should),
        use ``index_iter`` instead of the standard ``iter``
        method to iterate over all elements. This ensures that
        ``get_element_by_id`` works.
        """
        for _ in self.index_iter():
            pass

    def _add_to_id_index(self, element):
        """Builds the default ID index for get_element_by_id"""
        xmlid = element.get("{%s}id" % ns["xml"])
        if xmlid is not None:
            self._ids[xmlid] = element
    
    def get_element_by_id(self, xmlid):
        """Return element with given ID"""
        ret = self._ids.get(xmlid)
        if ret is None:
            raise TransformerNotFoundError(u"ID %s not found." % xmlid)
        return ret

    def _transform_document(self):
        ret = self._transform_node(self.root)
        for node in self.front_nodes:
            tag = node.tag
            if ((tag is et.PI and not self.skip_pis)
                    or (tag is et.Comment and not self.skip_comments)):
                self._addprevious(ret, node)
        return ret

    def _addprevious(self, target, node):
        """
        Add ``node`` before ``target`` if ``target`` is an element.
        If it is a list, just add the ``node`` as the first element of the
        list.
        """
        if isinstance(target, list):
            target.insert(0, node)
        else:
            target.addprevious(node)

    def _transform_node(self, node):
        """Generic node transformation."""
        if node is None:
            return self._transform_none()
        if isinstance(node, TextNode):
            return self._transform_text(node)
        node_type = node.tag
        if node_type is et.Comment:
            if self.skip_comments:
                return None
            else:
                return self._transform_comment(node)
        elif node_type is et.PI:
            if self.skip_pis:
                return None
            else:
                return self._transform_pi(node)
        else:
            return self._transform_element(node)

    def _transform_comment(self, comment):
        """Hook to transform comment node. Default is deepcopy."""
        ret = deepcopy(comment)
        ret.tail = None
        return ret

    def _transform_pi(self, processing_instruction):
        """Hook to transform processing instruction. Default is deepcopy."""
        ret = deepcopy(processing_instruction)
        ret.tail = None
        return ret

    @staticmethod
    def _append_to(target, stuff):
        """Append ``stuff`` to ``target``"""
        if stuff is None:
            return target
        if isinstance(target, list):
            if isinstance(stuff, list):
                target.extend(stuff)
            else:
                target.append(stuff)
        else:
            if isinstance(stuff, (str, unitext)):
                if len(target) == 0:
                    newtext = (target.text or "") + stuff
                    target.text = newtext
                else:
                    newtail = (target[-1].tail or "") + stuff
                    target[-1].tail = newtail
            elif isinstance(stuff, list):
                flattened = Transformer._flatten(stuff)
                for item in flattened:
                    Transformer._append_to(target, item)
            else:
                target.append(stuff)
        return target

    @staticmethod
    def _flatten(wild_list):
        """Take a wild list consisting of elements
        (probably without tail -- room for more
        optimization?) and texts and prepare them for
        easy adding. The rationale is that it will save
        a lot of time if we already have eliminated the
        texts as they can all be added as tails.
        """
        ret = []
        wild_list = [x for x in wild_list if x is not None]
        max = len(wild_list)
        i = 0
        item = None
        while i < max:
            if item is None:
                item = wild_list[i]
            nxt = None if i + 1 == max else wild_list[i + 1]
            if isinstance(item, (str, unitext)):
                if nxt is not None:
                    if isinstance(nxt, (str, unitext)):
                        item += nxt
                        i += 1
                    else:
                        ret.append(item)
                        item = None
                        i += 1
                else:
                    i += 1
                    ret.append(item)
                    item = None
            elif isinstance(item, (et._Element)):
                if nxt is not None:
                    if isinstance(nxt, (str, unitext)):
                        item.tail = (item.tail or "") + nxt
                        i += 1
                    else:
                        ret.append(item)
                        item = None
                        i += 1
                else:
                    i += 1
                    ret.append(item)
                    item = None
            elif isinstance(item, (list)):
                new_list = Transformer._flatten(item)
                wild_list = wild_list[0:i] + new_list + wild_list[i + 1:]
                max = len(wild_list)
                item = None
            else:
                raise TransformerError("Unknown type: " + str(type(item)))
        return ret

    def _transform_element(self, element):
        """Transform of an element
        
        This is the main dispatcher. Here transformation paths
        will fork depending on the element and its position in
        the original tree.

        The default is to just call the default transformtion,
        which basically produces a copy of the element.
        """
        convenience_method = self._find_default_method(element)
        if convenience_method is not None:
            return convenience_method(element)
        return self._default_element_transformation(element)

    def _find_default_method(self, element):
        name = strip_namespace_from_tagname(element.tag)
        name = "_convert_" + name
        return getattr(self, name, None)

    def _default_element_transformation(self, element):
        """Default transformation of an element.

        This produces basically a copy of the element and
        applies ``_transform_node`` to all its children.
        """
        ret = self._create_target_element(element)
        self._transform_attributes(element, ret)
        self._append_to(ret, self._transform_children(element))
        return ret

    def _create_target_element(self, element):
        """Create a target element for transformation"""
        if self.strip_namespaces:
            qn = et.QName(element)
            return et.Element(qn.localname)
        else:
            return et.Element(element.tag, nsmap=element.nsmap)

    def _transform_attributes(self, element, target):
        """Hook for transforming attributes"""
        for (a, v) in element.attrib.items():
            target.set(a, v)

    def _transform_children(self, element):
        """Transform all children of ``element`` and append to ``target``"""
        ret = []
        for child_node in AllChildNodesIterator(element):
            if not child_node in self.skip_nodes:
                # ret.append(self._transform_node(child_node))
                self._append_to(ret, self._transform_node(child_node))
        return ret

    def _transform_text(self, text_node):
        """Hook to work with TextNodes
        """
        if text_node.empty:
            return None
        return text_node.text

    def _transform_none(self):
        """Hook for transforming None.

        Some Transformers might want to return empty string instead.
        """
        return None

    def _copy(self, node, skip_comments=False, skip_pis=False):
        """Return copy of elmeent
        
        The default implementation is to return a
        deepcopy of the element, but you can override
        it with your idea of a copy.
        """
        return deepcopy(node)

    def _post_processing(self, doc):
        """Hook for finishing touches"""
        return doc

class Indenter(object):
    """
    Indenter for xml files.
    """

    import re

    re_lbr = re.compile(r"\s*\n+\s*")
    re_spc = re.compile(r" +")

    def __init__(self, document, block=[],
            b_wrap_text=False, textwidth=72,
            shiftwidth=2, initial_indentation_level=0,
            honor_xml_space=True):
        """
        Initialize
        """
        self.doc = document
        self.block = []
        self.block[:] = block
        self.honor_xml_space = honor_xml_space
        self.xml_space = "default"  # other possible value: preserve
        self.level = initial_indentation_level
        self.shiftwidth = shiftwidth
        self.textwidth = textwidth
        self.b_wrap = b_wrap_text

    def __repr__(self):
        return u"Indenter({})".format(self.doc)

    def __str__(self):
        return self.__repr__()

    def indent(self):
        """
        Do indentation for document (in place).
        """
        rootel = self.doc
        if isinstance(self.doc, et._ElementTree):
            rootel = self.doc.getroot()
        self.indent_element(rootel)

    @staticmethod
    def startswith_linebreak(e):
        """
        Tests if element text starts with some linebreak.
        """
        for c in (e.text or ""):
            if not c.isspace():
                return False
            if c == "\n":
                return True
        return False

    @staticmethod
    def endswith_linebreak(e):
        """
        Tests if element (text or last child's tail) ends with some linebreak.
        """
        if len(e) == 0:
            txt = (e.text or "")
        else:
            txt = (e[-1].tail or "")
        for i in range(len(txt) - 1, -1, -1):
            c = txt[i]
            if not c.isspace():
                return False
            if c == "\n":
                return True
        return False

    def normalize(self, s, last_element=False):
        """
        Normalize spaces (line breaks).
        """
        if s is None:
            return s
        ret = self.re_spc.sub(" ", s)
        if not last_element:
            ret = self.re_lbr.sub("\n" + " "*self.level*self.shiftwidth, ret)
        else:
            ret = self.re_lbr.sub("\n" + \
                    " "*(self.level - 1)*self.shiftwidth, ret)
        return ret

    def indent_element(self, e):
        """Indent given element"""
        self.xml_space = e.get("{%s}space" % ns["xml"], self.xml_space)
        if e.tag in self.block:
            self.level += 1
        if self.xml_space == "preserve" and self.honor_xml_space:
            for subel in e:
                current_xml_space = self.xml_space
                self.indent_element(subel)
                self.xml_space = current_xml_space
            return
        b_lbr_at_end = False
        e.text = self.normalize(e.text)
        if self.startswith_linebreak(e):
            b_lbr_at_end = True
        else:
            if len(e) > 0:
                subel = e[0]
                if subel.tag in self.block and (e.text or "").strip() == "":
                    e.text = "\n" + (" "*(self.level*self.shiftwidth))
                    b_lbr_at_end = True
        for subel in e:
            current_xml_space = self.xml_space
            self.indent_element(subel)
            self.xml_space = current_xml_space
            if (subel.tail or "").strip() == "" and \
                    self.is_next_block(subel):
                subel.tail = "\n"
            if subel.getnext() is None:
                subel.tail = self.normalize(subel.tail, last_element=True)
            else:
                subel.tail = self.normalize(subel.tail)
        if b_lbr_at_end:
            if len(e) == 0:
                txt = (e.text or "").rstrip()
                txt = txt + "\n" + (" "*(self.level - 1)*self.shiftwidth)
                e.text = txt
            else:
                tail = (e[-1].tail or "").rstrip()
                tail = tail + "\n" + (" "*(self.level - 1)*self.shiftwidth)
                e[-1].tail = tail
        if e.tag in self.block:
            self.level -= 1

    def is_next_block(self, e):
        """
        Is next sibling block level element?
        """
        nxt = e.getnext()
        if nxt is None:
            return False
        if nxt.tag in self.block:
            return True
        return False

class XMLTestCase(unittest.TestCase):

    def runTest(self):
        pass

    def assertXmlEqual(self, got, want):
        if isinstance(got, (et._Element, et._ElementTree)):
            got = et.tostring(got).decode()
        if isinstance(want, (et._Element, et._ElementTree)):
            want = et.tostring(want).decode()
        checker = LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(Example("", want), got, 0)
            raise AssertionError(message)

def get_text(el, skip_els=[], repl=[]):
    """
    Return text content

    - ``el``: element to get text from
    - ``skip_els``: list of tags to skip
      If you specify ``"*"`` then all tags will be skipped.
    - ``repl``: list of replacement strings for skipped tags
    """
    b_skip_all = False
    if skip_els == "*":
        b_skip_all = True
    elif not isinstance(skip_els, (list, tuple)):
        skip_els = [skip_els]
    if not isinstance(repl, (list, tuple)):
        repl = [repl]
    while len(repl) < len(skip_els):
        repl.append("")
    ret = []
    ret.append(el.text or "")
    for subel in el.getchildren():
        if not subel.tag in skip_els and not b_skip_all and \
           not subel.tag == et.ProcessingInstruction and \
           not subel.tag == et.Comment:
            ret.append(get_text(subel, skip_els, repl))
        else:
            if b_skip_all:
                ret.append(repl[0])
            elif subel.tag != et.ProcessingInstruction and \
               subel.tag != et.Comment:
                ret.append(repl[skip_els.index(subel.tag)])
        ret.append(subel.tail or "")
    ret = "".join(ret)
    return ret

def goto(el, pos, skip_els=[]):
    """
    Goto to character position within element
    
    Return tuple: (subelement, text_or_tail, pos)
    If positioning is not possible, the return value will be:
    (None, None, number of available characters in ``el``).
    """
    b_skip_all = False
    if skip_els == "*":
        b_skip_all = True
    elif not isinstance(skip_els, (list, tuple)):
        skip_els = [skip_els]
    # txt = get_text(el, skip_els)
    # First step: Build a document structure.
    # t_struct = [(el, text_or_tail, txt), ...]
    # This is according to the way we iterate through
    # a node in get_text().
    t_struct = get_t_struct(el, skip_els)
    realcnt = -1
    waitforit = None
    if pos == 0:
        # waitforit = (t_struct[0][0], TEXT, 0) 
        waitforit = (next(t_struct)[0], TEXT, 0) 
    for t in t_struct:
        length = len(t[2])
        if length > 0:
            realcnt += length
            if realcnt >= pos:
                return (t[0], t[1], pos + length - realcnt - 1)
            elif realcnt == pos - 1:
                if waitforit is None:
                    waitforit = (t[0], t[1], length)
    if waitforit is not None:
        return waitforit
    else:
        return (None, None, realcnt + 1)
        
def get_t_struct(el, skip_els=[]):
    """Generate list of text parts contained in ``el`` in document order.

    Yield:
        [(el, text_or_tail, txt), ...]
    """
    b_skip_all = False
    if skip_els == "*":
        b_skip_all = True
    elif not isinstance(skip_els, (list, tuple)):
        skip_els = [skip_els]
    txt = el.text or ""
    t_struct = [(el, TEXT, txt)]
    yield (el, TEXT, txt)
    for subel in el:
        if (not subel.tag in skip_els and not b_skip_all and 
           not subel.tag == et.ProcessingInstruction and 
           not subel.tag == et.Comment):
            for ts in get_t_struct(subel, skip_els):
                yield ts
        tail = subel.tail or ""
        yield (subel, TAIL, tail)

def delete(el):
    """
    Delete element without losing its tail
    """
    parent = el.getparent()
    if parent == None:
        raise XMLHelperError("Cannot delete root element.")
    if el.tail:
        pos = parent.index(el)
        if pos==0:
            parent.text = "%s%s" % ((parent.text or ""), el.tail)
        else:
            append_to = parent[pos - 1]
            append_to.tail = "%s%s" % ((append_to.tail or ""), el.tail)
    parent.remove(el)

def insert_at(el, new_el, pos, skip_els=[]):
    """
    Inserts element ``new_el`` at text position ``pos``.

    With ``skip_els`` you can specify which elements to skip
    while counting letters.

    Returns newly inserted element.
    """
    subelement, text_or_tail, subpos = goto(el, pos, skip_els)
    if subelement is None:
        raise XMLHelperError("Cannot go to pos %d in element <%s>." %
                             (pos, el.tag))
    if text_or_tail == TEXT:
        return insert_into_text(subelement, new_el, subpos)
    elif text_or_tail == TAIL:
        return insert_into_tail(subelement, new_el, subpos)

def insert_into_text(el, new_el, pos):
    """
    Insert ``new_el`` into text of element ``el`` at ``pos``

    Returns new_el
    """
    if el.text:
        el.text, rest = (el.text[0:pos], el.text[pos:])
    else:
        rest = ""
    if new_el.tail:
        new_el.tail = "%s%s" % (new_el.tail, rest)
    else:
        new_el.tail = rest
    el.insert(0, new_el)
    return new_el

def insert_into_tail(el, new_el, pos):
    """
    Insert ``new_el`` into tail of element ``el`` at ``pos``

    Returns new_el
    """
    if el.tail:
        el.tail, rest = (el.tail[0:pos], el.tail[pos:])
    else:
        rest = ""
    if new_el.tail:
        new_el.tail = "%s%s" % (new_el.tail, rest)
    else:
        new_el.tail = rest
    parent = el.getparent()
    idx = parent.getchildren().index(el)
    parent.insert(idx + 1, new_el)
    return new_el

def goto_next_char(el, text_or_tail, pos, container, skip_els=[]):
    """
    Move ahead until we find a real character
    (or are at the end of container)
    """
    b_skip_all = False
    if skip_els == "*":
        b_skip_all = True
    elif not isinstance(skip_els, (list, tuple)):
        skip_els = [skip_els]
    if not container in el.xpath("ancestor-or-self::*"):
        raise XMLHelperError("Element <%s> not in container <%s>." %\
                              (el.tag, container.tag))
    if text_or_tail == TEXT:
        text = el.text or ""
        if pos < len(text):
            return el, TEXT
        # the trivial case did not work
        if len(el) > 0:
            subel = el.getchildren()[0]
            if not b_skip_all and not subel.tag in skip_els:
                newel, newtext_or_tail = goto_next_char(subel, TEXT, 0,
                                                        subel, skip_els)
                if not newel is None:
                    return newel, newtext_or_tail
            # nothing found inside subelement, look at tail
            # The following call goes through the tail of the
            # subelement and through all following sibling subelements,
            # thus we need no further subelements
            newel, newtext_or_tail = goto_next_char(subel, TAIL,
                                                    0, el, skip_els)
            if not newel is None:
                return newel, newtext_or_tail
        pos = 0
    # now we must go on with the tail of this element
    # first check container
    if container == el:
        return None, None
    tail = el.tail or ""
    if pos < len(tail):
        return el, TAIL
    # the trivial case did not work
    parent = el.getparent()
    # if parent is None:
    #     # NB: This cannot happen.
    #     return None, None
    idx = parent.index(el)
    if idx + 1 < len(parent):
        nextel = parent[idx + 1]
        if b_skip_all or nextel.tag in skip_els:
            newel, newtext_or_tail = goto_next_char(nextel, TAIL, 0,
                                                    parent, skip_els)
        else:
            newel, newtext_or_tail = goto_next_char(nextel, TEXT, 0,
                                                    parent, skip_els)
        if not newel is None:
            return newel, newtext_or_tail
    # nothing found so far, we need to go on with the parent's tail
    # if parent != container
    if parent == container:
        return None, None
    newel, newtext_or_tail = goto_next_char(parent, TAIL, 0,
                                            container, skip_els)
    if newel is not None:
        # need to check, if there is really text
        if newtext_or_tail == TEXT:
            txt = newel.text or ""
        else:
            txt = newel.tail or ""
        # if txt == "":
        #     # NB: This cannot happen.
        #     return None, None
        # else:
        return newel, newtext_or_tail
    return None, None

def count_characters(el, skip_els=[]):
    """
    Count characters in an element
    """
    b_skip_all = False
    if skip_els == "*":
        b_skip_all = True
    elif not isinstance(skip_els, (list, tuple)):
        skip_els = [skip_els]
    count = 0
    if el.text:
        count = len(el.text)
    for subel in el.getchildren():
        if not b_skip_all and not subel.tag in skip_els and \
           not subel.tag == et.ProcessingInstruction and\
           not subel.tag == et.Comment:
            count += count_characters(subel, skip_els)
        if subel.tail:
            count += len(subel.tail)
    return count

def remove_tags(el):
    """
    Remove enclosing tags, but keep content
    """
    parent = el.getparent()
    idx = parent.index(el)
    if idx == 0:
        txt = parent.text or ""
        parent.text = "%s%s" % (txt, el.text or "") 
    else:
        tail = parent[idx - 1].tail or ""
        parent[idx - 1].tail = "%s%s" % (tail, el.text or "")
    for subel in el.getchildren():
        parent.insert(idx, subel)
        idx += 1
    tail = el.tail or ""
    if idx == 0:
        txt = parent.text or ""
        parent.text = "%s%s" % (txt, el.tail or "") 
    else:
        tail = parent[idx - 1].tail or ""
        parent[idx - 1].tail = "%s%s" % (tail, el.tail or "")
    parent.remove(el)

def get_pos(el, skip_els=[]):
    """
    Get position of element in the text of the parent element
    """
    parent = el.getparent()
    if parent is None:
        raise XMLHelperError("Element %s has no parent." % el.tag)
    b_skip_all = False
    if skip_els == "*":
        b_skip_all = True
    elif not isinstance(skip_els, (list, tuple)):
        skip_els = [skip_els]
    idx = parent.index(el)
    if idx == 0:
        if parent.text:
            return len(parent.text)
        else:
            return 0
    if parent.text:
        pos = len(parent.text)
    else:
        pos = 0
    for subel in parent[0:idx]:
        if (not b_skip_all) and (not subel.tag in skip_els):
            pos += len(get_text(subel, skip_els))
        if subel.tail:
            pos += len(subel.tail)
    return pos

def cut(from_el, to_el):
    """Cut passages of document"""
    # @@@TODO: There are too many calls to xpaths
    folls = from_el.xpath("following::*")
    if not to_el in folls:
        raise XMLHelperError("Element ``from_el`` (%s) not before "\
                "element ``to_el`` (%s) in document order." %\
                (from_el.tag, to_el.tag))
    from_el.tail = None
    for el in folls:
        if el == to_el:
            break
        if to_el in el.xpath("descendant::*"):
            el.text = None
        else:
            el.text = None
            el.tail = None
            remove_tags(el)
    for el in from_el.xpath("ancestor::*"):
        if not to_el in el.xpath("descendant::*"):
            el.tail = None
    delete(from_el)
    delete(to_el)
    return

def rstrip(el, skip_els=[]):
    """rstrip a given element"""
    b_skip_all = False
    if skip_els == "*":
        b_skip_all = True
    elif not isinstance(skip_els, (list, tuple)):
        skip_els = [skip_els]
    txt = get_text(el, skip_els)
    if txt != txt.rstrip():
        # first deal with children
        children = el.getchildren()
        current_index = len(el) - 1
        while current_index != -1:
            sibling = children[current_index]
            sibling.tail = (sibling.tail or "").rstrip()
            if sibling.tail == "":
                if not sibling.tag in skip_els and \
                        not b_skip_all:
                    sibling = rstrip(sibling)
                    if get_text(sibling) == "":
                        current_index -= 1
                    else:
                        return el
                else:
                    current_index -= 1
            else:
                return el
        # Now we need to check, if the text of the element
        # itself needs be rstripped.
        txt = get_text(el)
        if txt != txt.rstrip():
            el.text = el.text.rstrip()
            if el.text == "":
                el.text = None
    return el

def lstrip(el, skip_els=[]):
    """lstrip a given element"""
    b_skip_all = False
    if skip_els == "*":
        b_skip_all = True
    elif not isinstance(skip_els, (list, tuple)):
        skip_els = [skip_els]
    if (el.text or ""):
        el.text = el.text.lstrip()
    if len(el) == 0:
        return el
    if (el.text or "") == "":
        # OK, we need to go on with the children
        for subel in el:
            if not (subel.tag in skip_els or b_skip_all):
                lstrip(subel)
                txt = get_text(subel, skip_els)
            else:
                txt = ""
            if txt == "":
                if (subel.tail or ""):
                    subel.tail = subel.tail.lstrip()
                if (subel.tail or ""):
                    break
            else:
                break
    return el

def strip(el, skip_els=[]):
    """
    Convenience method: combines lstrip() and rstrip()
    """
    lstrip(el, skip_els)
    rstrip(el, skip_els)
    return el

def move_element(src, target):
    """
    Move complete element ``src`` with all content to ``target``
    
    Moved will be ``text``, all subelements, tagname, attributes.
    The source element will be removed. The target element will
    be renamed accordingly. Any present attributes and subelements
    will be deleted.
    """
    # sanity check
    if src in target.xpath("ancestor-or-self::*"):
        raise XMLHelperError("Target <%s> contained in source <%s>." %\
                             (target.tag, src.tag))
    # clean target
    for att in target.attrib:
        del(target.attrib[att])
    target.tag = src.tag
    for i in range(0, len(target)):
        del(target[i])
    # text
    target.text = src.text
    # subelements
    for subel in src.getchildren():
        target.append(subel)
    # attributes
    for att in src.attrib:
        target.set(att, src.get(att))
    # remove src
    delete(src)
    
def move_element_to_pos(src, target, text_or_tail, pos):
    """
    Move element ``src`` to the given target position.
    
    Return newly created element (as it will effectively
    be a copy of ``src``).
    """
    # create target element
    new_el = et.Element("target")
    if text_or_tail == TEXT:
        insert_into_text(target, new_el, pos)
    else:
        insert_into_tail(target, new_el, pos)
    # move source to target with ``move_element``
    move_element(src, new_el)
    return new_el

def move_element_to_textpos(src, target, textpos, skip_els=[]):
    """
    Move ``src`` to ``textpos`` in ``target``.
    
    Return newly created element (as it will effectively
    be a copy of ``src``).
    """
    # create target element
    new_el = et.Element("target")
    insert_at(target, new_el, textpos, skip_els)
    # move
    move_element(src, new_el)
    return new_el

def wrap(new_el, target):
    """
    Wrap given new element ``new_el`` around ``target``
    """
    parent = target.getparent()
    if parent is None:
        raise XMLHelperError("Element <%s> has no parent (root element?)." %\
                              target.tag)
    idx = parent.index(target)
    parent.insert(idx, new_el)
    new_el.append(target)
    new_el.tail = target.tail
    target.tail = None

def collect(new_el, target_els):
    """
    Put all ``target_els`` into ``new_el``.
    
    ``new_el`` will be inserted at the position of the first target element.
    """
    if type(target_els) != list or len(target_els) == 0:
        raise XMLHelperError("``target_els`` must be non empty list " \
                             "of elements.")
    parent = target_els[0].getparent()
    if parent is None:
        raise XMLHelperError("Element <%s> has no parent (root element?)." %\
                              target_els[0].tag)
    idx = parent.index(target_els[0])
    parent.insert(idx, new_el)
    if len(target_els) > 1:
        for t in target_els[0:-1]:
            new_el.append(t)
    t = target_els[-1]
    parent = t.getparent()
    if parent is None:
        raise XMLHelperError("Element <%s> has no parent (root element?)." %\
                              t.tag)
    t = cut_element(t)
    new_el.append(t)
    
def span(start, end=None):
    """
    Wrap an element ``span`` around ``start`` and ``end``.
    
    If only ``start`` is given, just wrap a ``span`` around it.
    
    Return newly created element ``span``.
    """
    span = et.Element("span")
    if end is None:
        wrap(span, start)
        return span
    parent = start.getparent()
    if not parent == end.getparent():
        raise XMLHelperError("Start and end elements must be siblings.")
    idx1 = parent.index(start)
    idx2 = parent.index(end)
    if idx1 > idx2:
        raise XMLHelperError("Start element must be before end element.")
    parent.insert(idx1, span)
    for el in parent[idx1 + 1:idx2 + 1]:
        span.append(el)
    # Now the last element, which has to be cut.
    # The position of this element is now ``idx1 + 1``.
    lastel = cut_element(parent[idx1 + 1])
    span.append(lastel)
    return span

def cut_element(el):
    """
    Remove ``el`` from document and return it without its tail.
    """
    parent = el.getparent()
    if parent is None:
        raise XMLHelperError("Element <%s> has no parent (root element?)." %\
                             el.tag)
    idx = parent.index(el)
    if idx == 0:
        parent.text = (parent.text or "") + (el.tail or "")
    else:
        prev = parent[idx - 1]
        prev.tail = (prev.tail or "") + (el.tail or "")
    parent[:] = parent[0:idx] + parent[idx + 1:]
    el.tail = None
    return el

def copy(el):
    """
    Return copy of the given element.
    """
    storetail = el.tail
    el.tail = None
    ret = et.fromstring(et.tostring(el))
    el.tail = storetail
    return ret

def split(el):
    """
    Split parent of ``el`` so that ``el`` is at the same level as its parent.
    
    ``<a>abc<b/>def</a>`` becomes ``<a>abc</a><b/><a>def</a>``.
    """
    parent = el.getparent()
    if parent is None:
        raise XMLHelperError("Element <%s> has no parent." % el.tag)
    grandparent = parent.getparent()
    if grandparent is None:
        raise XMLHelperError("Element <%s> has no grandparent." % el.tag)
    cpp = copy(parent)
    idx = parent.index(el)
    cpp.text = el.tail
    cpp.tail = parent.tail
    parent.tail = None
    del cpp[:]
    el.tail = None
    count = len(parent) - idx - 1
    while count > 0:
        cpp.append(parent[idx + 1])
        count -= 1
    idx2 = grandparent.index(parent)
    grandparent.insert(idx2 + 1, cpp)
    grandparent.insert(idx2 + 1, el)
    return

def get_xpath_index(el):
    """
    Get the index of ``el`` within its siblings sharing the same tag name.
    """
    if isinstance(el, TextNode) and el.empty:
        raise XMLHelperError("Cannot determine XPath for empty TextNode.")
    parent = el.getparent()
    if parent is None:
        return 1
    cnt = 1
    for child in AllChildNodesIterator(parent):
        if child == el:
            return cnt
        if isinstance(el, TextNode):
            if isinstance(child, TextNode):
                if not child.empty:
                    cnt += 1
        elif child.tag == el.tag:
            cnt += 1

def get_xpath(el):
    """
    Return an xpath of given ``el`` relative to document root
    """
    ret = []
    parent = el.getparent()
    current_el = el
    while parent is not None:
        # pos = parent.index(current_el)
        pos = get_xpath_index(current_el)
        xpath_component = "text()" if isinstance(current_el, TextNode)\
            else current_el.tag
        ret.append((xpath_component, pos))
        current_el = parent
        parent = current_el.getparent()
    ret.append((current_el.tag, 1))  # is always the root element
    ret = ["%s[%d]" % x for x in ret]
    ret.reverse()
    return "/" + "/".join(ret)

def delat(el, attname):
    """
    Delete attribute
    """
    try:
        del el.attrib[attname]
    except KeyError:
        pass

def switch(el1, el2):
    """
    Switch places of ``el1`` and ``el2``.
    """
    if el1 is el2:
        return
    parent1 = el1.getparent()
    if parent1 is None:
        raise XMLHelperError("Cannot switch with root element.")
    parent2 = el2.getparent()
    if parent2 is None:
        raise XMLHelperError("Cannot switch with root element.")
    if contains(el1, el2) or contains(el2, el1):
        raise XMLHelperError("Cannot switch nested elements.")
    pos1 = parent1.index(el1)
    pos2 = parent2.index(el2)
    parent1.insert(pos1, el2)
    # We need the following call to remove in order to keep positioning
    # correct, if both elements are children of the same parent.
    parent1.remove(el1)
    parent2.insert(pos2, el1)
    tmp = el1.tail
    el1.tail = el2.tail
    el2.tail = tmp

def contains(el1, el2):
    """
    Is ``el2`` descendant of ``el1``?
    """
    parent = el2.getparent()
    while parent is not None:
        if parent is el1:
            return True
        parent = parent.getparent()
    return False

def strip_namespace_from_tagname(tagname):
    if tagname.startswith("{"):
        endpos = tagname.find("}")
        return tagname[endpos+1:]
    return tagname
