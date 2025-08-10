"""Report generator (RSS and Markdown) for ArxivAutoJob."""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates a complete RSS feed and a Markdown summary by scanning analysis files."""
    
    def __init__(self, rss_output_file: str = "download/rss.xml"):
        self.rss_output_file = rss_output_file
        self.feed_title = "ArxivAutoJob - AI/ML 论文更新"
        self.feed_description = "每周自动更新的AI和机器学习领域最新论文摘要"
        self.feed_link = "https://github.com/jchenibm/ArxivAutoJob"
        self.papers: List[Dict[str, Any]] = []

    def _load_papers_from_analysis_files(self):
        """Loads all paper data from the analysis JSON files in the download directory."""
        if self.papers:
            return

        logger.info("Scanning for analysis files to load paper data...")
        all_papers = []
        download_dir = Path("download")
        
        if not download_dir.exists():
            logger.warning("Download directory not found. Cannot load paper data.")
            return
            
        for json_file in download_dir.glob("*_analysis.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                
                base_filename = json_file.stem.replace("_analysis", "")
                parts = base_filename.split(' - ', 1)
                paper_id = parts[0]
                
                md_file = download_dir / f"{base_filename}.md"
                
                content = ""
                if md_file.exists():
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    content = analysis_data.get('detailed_summary', 'No content available.')
                
                paper_info = {
                    'id': paper_id,
                    'title': analysis_data.get('title', paper_id),
                    'analysis': analysis_data,
                    'content': content,
                    'pdf_link': f"https://arxiv.org/pdf/{paper_id}",
                    'pub_date': analysis_data.get('published', datetime.now().isoformat())
                }
                all_papers.append(paper_info)
            except Exception as e:
                logger.error(f"Error processing file {json_file}: {str(e)}")
        
        self.papers = all_papers
        logger.info(f"Loaded data for {len(self.papers)} papers.")

    def regenerate_complete_feed(self):
        """Regenerates the complete RSS feed from all analysis files."""
        self._load_papers_from_analysis_files()
        logger.info("Generating RSS feed...")
        rss_content = self._generate_rss_xml()
        self._save_file(rss_content, self.rss_output_file)
        logger.info(f"RSS feed successfully saved to {self.rss_output_file}")

    def generate_markdown_summary(self, output_filename: str = "summary.md"):
        """Generates a single Markdown file summarizing all processed papers."""
        self._load_papers_from_analysis_files()
        output_path = Path("download") / output_filename
        logger.info(f"Generating Markdown summary at {output_path}...")

        summary_content = [f"# Arxiv Paper Summary - {datetime.now().strftime('%Y-%m-%d')}\n\n"]
        self.papers.sort(key=lambda p: p.get('pub_date', ''), reverse=True)

        for paper in self.papers:
            paper_id = paper.get('id', 'N/A')
            title = paper.get('title', 'No Title')
            pdf_link = paper.get('pdf_link', f"https://arxiv.org/abs/{paper_id}")
            analysis = paper.get('analysis', {})

            summary_content.append(f"## [{title}]({pdf_link})\n\n")
            summary_content.append(f"**ID**: `{paper_id}`\n\n")

            def format_section(title, content):
                if not content: return ""
                if isinstance(content, list):
                    items = "\n".join(f"- {item}" for item in content if item)
                    return f"### {title}\n{items}\n\n" if items else ""
                return f"### {title}\n{content}\n\n"

            summary_content.append(format_section("摘要 (Detailed Summary)", analysis.get('detailed_summary')))
            summary_content.append(format_section("主要贡献 (Contributions)", analysis.get('contributions')))
            summary_content.append(format_section("技术方法 (Methods)", analysis.get('methods')))
            summary_content.append(format_section("主要结论 (Conclusions)", analysis.get('conclusions')))
            summary_content.append(format_section("GitHub链接 (GitHub Links)", analysis.get('github_links')))
            summary_content.append("---\n\n")

        self._save_file("".join(summary_content), str(output_path))
        logger.info(f"Markdown summary successfully saved to {output_path}")

    def _generate_rss_xml(self) -> str:
        """Generates the RSS XML string from the loaded papers."""
        rss = ET.Element('rss', version='2.0', attrib={"xmlns:content": "http://purl.org/rss/1.0/modules/content/"})
        channel = ET.SubElement(rss, 'channel')
        
        ET.SubElement(channel, 'title').text = self.feed_title
        ET.SubElement(channel, 'description').text = self.feed_description
        ET.SubElement(channel, 'link').text = self.feed_link
        ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        self.papers.sort(key=lambda p: p.get('pub_date', ''), reverse=True)
        
        for paper in self.papers:
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = paper.get('title', paper.get('id', 'Unknown Paper'))
            
            description_content = self._format_paper_description(paper)
            ET.SubElement(item, 'description').text = f"<![CDATA[{description_content}]]>"
            ET.SubElement(item, 'link').text = paper.get('pdf_link', f"https://arxiv.org/abs/{paper.get('id', '')}")
            ET.SubElement(item, 'guid', isPermaLink="false").text = paper.get('id', '')
            
            pub_date_str = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            iso_date = paper.get('pub_date')
            if iso_date:
                try:
                    dt_obj = datetime.fromisoformat(str(iso_date).replace('Z', '+00:00'))
                    pub_date_str = dt_obj.strftime("%a, %d %b %Y %H:%M:%S GMT")
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse date '{iso_date}' for paper {paper.get('id')}. Using current time.")
            ET.SubElement(item, 'pubDate').text = pub_date_str

        rough_string = ET.tostring(rss, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def _format_paper_description(self, paper_info: Dict[str, Any]) -> str:
        """Formats paper information for the RSS item description."""
        analysis = paper_info.get('analysis', {})
        description_parts = []
        fields = {
            "摘要": analysis.get('detailed_summary'),
            "主要贡献": analysis.get('contributions'),
            "技术方法": analysis.get('methods'),
            "主要结论": analysis.get('conclusions'),
            "GitHub链接": analysis.get('github_links')
        }
        for title, content in fields.items():
            if not content: continue
            if isinstance(content, list):
                if not all(item for item in content): continue
                list_items = ''.join([f'<li>{item}</li>' for item in content])
                description_parts.append(f'<h3>{title}</h3><ul>{list_items}</ul>')
            else:
                description_parts.append(f'<h3>{title}</h3><p>{content}</p>')
        return ''.join(description_parts)

    def _save_file(self, content: str, output_path: str):
        """Saves content to a file."""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to save file to {output_path}: {e}")
