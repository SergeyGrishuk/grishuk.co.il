"""Tests for the custom Markdown renderer."""
from main import CustomRenderer, markdown_processor
import mistune


def make_renderer():
    return mistune.create_markdown(renderer=CustomRenderer())


class TestCustomRendererLinks:
    def test_external_http_link_gets_target_blank_and_rel(self):
        md = make_renderer()
        result = md("[click](http://example.com)")
        assert 'target="_blank"' in result
        assert 'rel="noopener noreferrer"' in result
        assert 'href="http://example.com"' in result

    def test_external_https_link_gets_target_blank_and_rel(self):
        md = make_renderer()
        result = md("[click](https://example.com)")
        assert 'target="_blank"' in result
        assert 'rel="noopener noreferrer"' in result

    def test_protocol_relative_link_gets_target_blank_and_rel(self):
        md = make_renderer()
        result = md("[click](//example.com)")
        assert 'target="_blank"' in result
        assert 'rel="noopener noreferrer"' in result

    def test_relative_link_gets_target_blank_without_rel(self):
        md = make_renderer()
        result = md("[click](/page)")
        assert 'target="_blank"' in result
        assert "noopener" not in result

    def test_link_text_preserved(self):
        md = make_renderer()
        result = md("[Hello World](https://example.com)")
        assert "Hello World" in result


class TestCustomRendererHeadings:
    def test_heading_generates_id_slug(self):
        md = make_renderer()
        result = md("# Hello World")
        assert 'id="hello-world"' in result
        assert "<h1" in result

    def test_heading_strips_special_characters(self):
        md = make_renderer()
        result = md("## What's New?")
        assert 'id="whats-new"' in result

    def test_heading_level_preserved(self):
        md = make_renderer()
        result = md("### Sub Section")
        assert "<h3" in result
        assert "</h3>" in result

    def test_heading_collapses_multiple_dashes(self):
        md = make_renderer()
        result = md("# Hello   World")
        assert 'id="hello-world"' in result


class TestCustomRendererImages:
    def test_image_gets_center_class(self):
        md = make_renderer()
        result = md("![alt text](image.png)")
        assert 'class="center-image"' in result

    def test_image_preserves_src(self):
        md = make_renderer()
        result = md("![alt text](/images/photo.jpg)")
        assert 'src="/images/photo.jpg"' in result


class TestMarkdownProcessor:
    def test_bold_text(self):
        result = markdown_processor("**bold**")
        assert "<strong>bold</strong>" in result

    def test_italic_text(self):
        result = markdown_processor("*italic*")
        assert "<em>italic</em>" in result

    def test_code_block(self):
        result = markdown_processor("```\ncode\n```")
        assert "<code>" in result

    def test_inline_code(self):
        result = markdown_processor("`inline`")
        assert "<code>inline</code>" in result
