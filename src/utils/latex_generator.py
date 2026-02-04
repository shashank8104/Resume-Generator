"""LaTeX resume generation utilities"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import tempfile
import subprocess

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class LaTeXResumeGenerator:
    """Generate professional LaTeX resumes from structured data"""
    
    def __init__(self):
        self.templates_dir = Path("src/templates/latex")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_latex_resume(
        self, 
        resume_data: Dict[str, Any],
        template_style: str = "analyst",
        color_scheme: str = "blue"
    ) -> str:
        """
        Generate LaTeX resume code
        
        Returns:
            str: LaTeX source code
        """
        
        try:
            # Select template based on style
            if template_style == "analyst":
                latex_code = self._generate_analyst_template(resume_data, color_scheme)
            elif template_style == "academic":
                latex_code = self._generate_academic_template(resume_data, color_scheme)
            elif template_style == "modern":
                latex_code = self._generate_modern_template(resume_data, color_scheme)
            elif template_style == "classic":
                latex_code = self._generate_classic_template(resume_data, color_scheme)
            else:
                latex_code = self._generate_modern_template(resume_data, color_scheme)
                
            logger.info(f"LaTeX resume generated successfully with template: {template_style}")
            return latex_code
            
        except Exception as e:
            logger.error(f"Error generating LaTeX resume: {str(e)}")
            raise
    
    def _generate_modern_template(self, data: Dict[str, Any], color: str) -> str:
        """Generate modern LaTeX template using moderncv"""
        
        contact = data.get('contact_info', {})
        skills = data.get('skills', {})
        experience = data.get('experience', [])
        education = data.get('education', [])
        
        # Color scheme mapping
        color_codes = {
            "blue": "blue",
            "green": "green", 
            "red": "red",
            "purple": "purple",
            "orange": "orange"
        }
        
        selected_color = color_codes.get(color, "blue")
        
        # Split name for moderncv format
        full_name = contact.get('full_name', 'John Doe')
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else 'John'
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'Doe'
        
        latex_code = f"""\\documentclass[11pt,a4paper,sans]{{moderncv}}

% Modern CV theme and color
\\moderncvstyle{{banking}}
\\moderncvcolor{{{selected_color}}}

% Character encoding
\\usepackage[utf8]{{inputenc}}

% Adjust the page margins
\\usepackage[scale=0.75]{{geometry}}

% Personal data
\\name{{{first_name}}}{{{last_name}}}
\\title{{{data.get('summary', 'Professional Resume').split('.')[0] if data.get('summary') else 'Professional Resume'}}}
\\address{{{contact.get('location', '')}}}{{}}{{}}
\\phone[mobile]{{{contact.get('phone', '')}}}
\\email{{{contact.get('email', '')}}}"""

        # Add social links if available
        if contact.get('linkedin'):
            linkedin_clean = contact.get('linkedin', '').replace('https://linkedin.com/in/', '').replace('https://www.linkedin.com/in/', '')
            latex_code += f"\n\\social[linkedin]{{{linkedin_clean}}}"
        
        if contact.get('github'):
            github_clean = contact.get('github', '').replace('https://github.com/', '')
            latex_code += f"\n\\social[github]{{{github_clean}}}"

        latex_code += """

\\begin{document}
\\makecvtitle

"""

        # Professional Summary
        if data.get('summary'):
            latex_code += f"""% Professional Summary
\\section{{Professional Summary}}
\\cvitem{{}}{{{self._escape_latex(data.get('summary', ''))}}}

"""

        # Skills Section
        if skills:
            latex_code += "% Skills Section\n\\section{Technical Skills}\n"
            for category, skill_list in skills.items():
                if skill_list and isinstance(skill_list, list):
                    skills_text = ", ".join(skill_list)
                    category_clean = category.replace('_', ' ').title()
                    latex_code += f"\\cvitem{{{category_clean}}}{{{self._escape_latex(skills_text)}}}\n"
            latex_code += "\n"
        
        # Experience Section
        if experience:
            latex_code += "% Experience Section\n\\section{Professional Experience}\n"
            for exp in experience:
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', 'Present')
                date_range = f"{start_date}--{end_date}" if start_date else end_date
                
                position = self._escape_latex(exp.get('position', ''))
                company = self._escape_latex(exp.get('company', ''))
                
                latex_code += f"\\cventry{{{date_range}}}{{{position}}}{{{company}}}{{}}{{}}{{%\n"
                
                # Add job description as bullet points
                descriptions = exp.get('description', [])
                if descriptions and isinstance(descriptions, list):
                    latex_code += "\\begin{itemize}%\n"
                    for desc in descriptions[:4]:  # Limit to 4 bullet points
                        if desc and desc.strip():
                            latex_code += f"  \\item {self._escape_latex(desc.strip())}\n"
                    latex_code += "\\end{itemize}%\n"
                
                latex_code += "}\n\n"
        
        # Education Section
        if education:
            latex_code += "% Education Section\n\\section{Education}\n"
            for edu in education:
                grad_date = edu.get('graduation_date', '')
                degree = self._escape_latex(edu.get('degree', ''))
                institution = self._escape_latex(edu.get('institution', ''))
                gpa = edu.get('gpa', '')
                
                gpa_text = f" (GPA: {gpa})" if gpa else ""
                
                # Build the cventry line safely
                latex_code += "\\cventry{" + grad_date + "}{" + degree + "}{" + institution + "}{}{}{%\n" + gpa_text + "%\n}\n"
            latex_code += "\n"
        
        latex_code += "\\end{document}"
        
        return latex_code
    
    def _generate_academic_template(self, data: Dict[str, Any], color: str) -> str:
        """Generate academic-style LaTeX template"""
        
        contact = data.get('contact_info', {})
        
        latex_code = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{hyperref}}
\\usepackage{{xcolor}}

\\geometry{{margin=1in}}
\\definecolor{{headingcolor}}{{RGB}}{{0,84,159}}

% Remove page numbers
\\pagestyle{{empty}}

% Custom section formatting
\\usepackage{{titlesec}}
\\titleformat{{\\section}}{{\\color{{headingcolor}}\\Large\\bfseries}}{{}}{{0em}}{{}}[\\titlerule]

\\begin{{document}}

% Header with name and contact
\\begin{{center}}
    {{\\Huge\\bfseries {self._escape_latex(contact.get('full_name', 'John Doe'))}}} \\\\[0.5em]
    {self._escape_latex(contact.get('email', ''))} $\\bullet$ {self._escape_latex(contact.get('phone', ''))} $\\bullet$ {self._escape_latex(contact.get('location', ''))} \\\\
"""
        
        if contact.get('linkedin') or contact.get('website'):
            latex_code += f"    {self._escape_latex(contact.get('linkedin', ''))} $\\bullet$ {self._escape_latex(contact.get('website', ''))}\n"
        
        latex_code += """\\end{center}

\\vspace{1em}

"""

        # Professional Summary
        if data.get('summary'):
            latex_code += f"""\\section{{Research Interests}}
{self._escape_latex(data.get('summary', ''))}

"""

        # Skills Section
        skills = data.get('skills', {})
        if skills:
            latex_code += "\\section{Technical Expertise}\n\\begin{itemize}[leftmargin=*]\n"
            for category, skill_list in skills.items():
                if skill_list and isinstance(skill_list, list):
                    skills_text = ", ".join(skill_list)
                    category_clean = category.replace('_', ' ').title()
                    latex_code += f"  \\item \\textbf{{{category_clean}:}} {self._escape_latex(skills_text)}\n"
            latex_code += "\\end{itemize}\n\n"

        # Experience as "Research Experience"
        if data.get('experience'):
            latex_code += "\\section{Research Experience}\n"
            for exp in data.get('experience', []):
                position = self._escape_latex(exp.get('position', ''))
                company = self._escape_latex(exp.get('company', ''))
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', 'Present')
                
                latex_code += f"\\textbf{{{position}}} \\hfill {start_date}--{end_date} \\\\\n"
                latex_code += f"\\textit{{{company}}} \\\\\n"
                
                descriptions = exp.get('description', [])
                if descriptions and isinstance(descriptions, list):
                    latex_code += "\\begin{itemize}\n"
                    for desc in descriptions:
                        if desc and desc.strip():
                            latex_code += f"  \\item {self._escape_latex(desc.strip())}\n"
                    latex_code += "\\end{itemize}\n"
                latex_code += "\n"

        # Education
        if data.get('education'):
            latex_code += "\\section{Education}\n"
            for edu in data.get('education', []):
                degree = self._escape_latex(edu.get('degree', ''))
                institution = self._escape_latex(edu.get('institution', ''))
                grad_date = edu.get('graduation_date', '')
                gpa = edu.get('gpa', '')
                
                latex_code += f"\\textbf{{{degree}}} \\hfill {grad_date} \\\\\n"
                latex_code += f"\\textit{{{institution}}}"
                if gpa:
                    latex_code += f" \\hfill GPA: {gpa}"
                latex_code += " \\\\\n\n"
        
        latex_code += "\\end{document}"
        
        return latex_code
    
    def _generate_classic_template(self, data: Dict[str, Any], color: str) -> str:
        """Generate classic professional LaTeX template"""
        
        contact = data.get('contact_info', {})
        
        latex_code = f"""\\documentclass[10pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{hyperref}}

\\geometry{{margin=0.8in}}

% Remove page numbering
\\pagestyle{{empty}}

% Custom formatting
\\usepackage{{titlesec}}
\\titleformat{{\\section}}{{\\large\\bfseries}}{{}}{{0em}}{{}}[\\hrule height 1pt]

\\begin{{document}}

% Classic header
\\begin{{center}}
    {{\\LARGE\\textbf{{{self._escape_latex(contact.get('full_name', 'John Doe'))}}}}} \\\\[0.3em]
    {self._escape_latex(contact.get('location', ''))} \\\\
    {self._escape_latex(contact.get('phone', ''))} $\\cdot$ {self._escape_latex(contact.get('email', ''))}
\\end{{center}}

\\vspace{{0.5em}}

\\section{{OBJECTIVE}}
{self._escape_latex(data.get('summary', 'Seeking a challenging position to utilize professional skills and contribute to organizational success.'))}

"""
        
        # Skills
        if data.get('skills'):
            latex_code += "\\section{TECHNICAL SKILLS}\n"
            skills_list = []
            for category, skill_list in data.get('skills', {}).items():
                if skill_list and isinstance(skill_list, list):
                    category_clean = category.replace('_', ' ').title()
                    skills_text = ", ".join(skill_list)
                    skills_list.append(f"\\textbf{{{category_clean}:}} {self._escape_latex(skills_text)}")
            
            if skills_list:
                latex_code += "\\begin{itemize}[leftmargin=*]\n"
                for skill_item in skills_list:
                    latex_code += f"  \\item {skill_item}\n"
                latex_code += "\\end{itemize}\n\n"

        # Experience
        if data.get('experience'):
            latex_code += "\\section{PROFESSIONAL EXPERIENCE}\n"
            for exp in data.get('experience', []):
                position = self._escape_latex(exp.get('position', ''))
                company = self._escape_latex(exp.get('company', ''))
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', 'Present')
                
                latex_code += f"\\textbf{{{position}}} \\hfill {start_date} -- {end_date} \\\\\n"
                latex_code += f"\\textit{{{company}}} \\\\\n"
                
                descriptions = exp.get('description', [])
                if descriptions and isinstance(descriptions, list):
                    latex_code += "\\begin{itemize}\n"
                    for desc in descriptions:
                        if desc and desc.strip():
                            latex_code += f"  \\item {self._escape_latex(desc.strip())}\n"
                    latex_code += "\\end{itemize}\n"
                latex_code += "\n"

        # Education
        if data.get('education'):
            latex_code += "\\section{EDUCATION}\n"
            for edu in data.get('education', []):
                degree = self._escape_latex(edu.get('degree', ''))
                institution = self._escape_latex(edu.get('institution', ''))
                grad_date = edu.get('graduation_date', '')
                
                latex_code += f"\\textbf{{{degree}}} \\hfill {grad_date} \\\\\n"
                latex_code += f"\\textit{{{institution}}} \\\\\n\n"
        
        latex_code += "\\end{document}"
        
        return latex_code

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        # LaTeX special characters that need escaping
        replacements = {
            '&': '\\&',
            '%': '\\%', 
            '$': '\\$',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '\\': '\\textbackslash{}'
        }
        
        result = text
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
            
        return result

    def parse_existing_latex(self, latex_content: str) -> Dict[str, Any]:
        """Parse existing LaTeX resume to extract data structure"""
        
        parsed_data = {
            'contact_info': {},
            'summary': '',
            'skills': {},
            'experience': [],
            'education': []
        }
        
        try:
            # Extract name (moderncv format)
            name_match = re.search(r'\\name\{([^}]+)\}\{([^}]*)\}', latex_content)
            if name_match:
                parsed_data['contact_info']['full_name'] = f"{name_match.group(1)} {name_match.group(2)}".strip()
            
            # Extract email
            email_match = re.search(r'\\email\{([^}]+)\}', latex_content)
            if email_match:
                parsed_data['contact_info']['email'] = email_match.group(1)
            
            # Extract phone
            phone_match = re.search(r'\\phone\[mobile\]\{([^}]+)\}', latex_content)
            if phone_match:
                parsed_data['contact_info']['phone'] = phone_match.group(1)
            
            # Extract address
            address_match = re.search(r'\\address\{([^}]+)\}', latex_content)
            if address_match:
                parsed_data['contact_info']['location'] = address_match.group(1)
            
            # Try to extract summary from cvitem
            summary_match = re.search(r'\\section\{.*[Ss]ummary.*\}[^\\]*\\cvitem\{\}\{([^}]+)\}', latex_content, re.DOTALL)
            if summary_match:
                parsed_data['summary'] = summary_match.group(1).strip()
            
            logger.info("LaTeX resume parsed successfully")
            
        except Exception as e:
            logger.error(f"Error parsing LaTeX resume: {str(e)}")
        
        return parsed_data

    def compile_latex_to_pdf(self, latex_code: str, output_name: str = "resume") -> Optional[str]:
        """Compile LaTeX code to PDF using pdflatex"""
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                tex_file = Path(temp_dir) / f"{output_name}.tex"
                pdf_file = Path(temp_dir) / f"{output_name}.pdf"
                
                # Write LaTeX code to file
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex_code)
                
                # Try to compile with pdflatex
                try:
                    result = subprocess.run([
                        'pdflatex', 
                        '-interaction=nonstopmode',
                        '-output-directory', temp_dir,
                        str(tex_file)
                    ], capture_output=True, text=True, cwd=temp_dir, timeout=30)
                    
                    if result.returncode == 0 and pdf_file.exists():
                        # Move PDF to permanent location
                        output_dir = Path("generated_resumes")
                        output_dir.mkdir(exist_ok=True)
                        final_pdf = output_dir / f"{output_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        
                        import shutil
                        shutil.copy(pdf_file, final_pdf)
                        logger.info(f"PDF compiled successfully: {final_pdf}")
                        return str(final_pdf)
                    else:
                        logger.warning(f"LaTeX compilation failed: {result.stderr}")
                        return None
                        
                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    logger.warning(f"LaTeX compiler not available: {str(e)}")
                    return None
                    
        except Exception as e:
            logger.error(f"PDF compilation error: {str(e)}")
            return None
    
    def _generate_analyst_template(self, resume_data: Dict[str, Any], color: str) -> str:
        """Generate resume in the user's custom analyst format"""
        personal_info = resume_data.get('personal_info', {})
        education = resume_data.get('education', {})
        skills = resume_data.get('technical_skills', {})
        projects = resume_data.get('projects', [])
        internships = resume_data.get('internships', [])
        achievements = resume_data.get('achievements', [])
        
        latex_code = f'''%-------------------------
% Resume in Latex
% Author : Jake Gutierrez
% Based off of: https://github.com/sb2nov/resume
% License : MIT
%------------------------
\\documentclass[a4paper,11pt]{{article}}

\\usepackage{{latexsym}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{titlesec}}
\\usepackage{{marvosym}}
\\usepackage[usenames,dvipsnames]{{color}}
\\usepackage{{verbatim}}
\\usepackage{{enumitem}}
\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage[english]{{babel}}
\\usepackage{{tabularx}}
\\usepackage{{fontawesome5}}
\\usepackage{{multicol}}
\\usepackage{{graphicx}}
\\usepackage{{svg}}
\\usepackage{{hyperref}} 
\\setlength{{\\multicolsep}}{{-3.0pt}}
\\setlength{{\\columnsep}}{{-1pt}}
\\input{{glyphtounicode}}

%----------FONT OPTIONS----------
% sans-serif
% \\usepackage[sfdefault]{{FiraSans}}
% \\usepackage[sfdefault]{{roboto}}
% \\usepackage[sfdefault]{{noto-sans}}
% \\usepackage[default]{{sourcesanspro}}

% serif
% \\usepackage{{CormorantGaramond}}
% \\usepackage{{charter}}

% \\RequirePackage{{fontawesome5}}

\\pagestyle{{fancy}}
\\fancyhf{{}} % clear all header and footer fields
\\fancyfoot{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}
\\setlength{{\\footskip}}{{10pt}} 

% Adjust margins
\\addtolength{{\\oddsidemargin}}{{-0.6in}}
\\addtolength{{\\evensidemargin}}{{-0.5in}}
\\addtolength{{\\textwidth}}{{1.19in}}
\\addtolength{{\\topmargin}}{{-.7in}}
\\addtolength{{\\textheight}}{{1.4in}}

\\urlstyle{{same}}

\\raggedbottom
\\raggedright
\\setlength{{\\tabcolsep}}{{0in}}

% Sections formatting
\\titleformat{{\\section}}{{
  \\vspace{{-4pt}}\\scshape\\raggedright\\large\\bfseries
}}{{}}{{0em}}{{}}[\\color{{black}}\\titlerule \\vspace{{-5pt}}]

% Ensure that generate pdf is machine readable/ATS parsable
\\pdfgentounicode=1

%-------------------------
% Custom commands
\\newcommand{{\\resumeItem}}[1]{{
  \\item\\small{{
    {{#1 \\vspace{{-2pt}}}}
  }}
}}

\\newcommand{{\\classesList}}[4]{{
    \\item\\small{{
        {{#1 #2 #3 #4 \\vspace{{-2pt}}}}
  }}
}}

\\newcommand{{\\resumeSubheading}}[4]{{
  \\vspace{{-2pt}}\\item
    \\begin{{tabular*}}{{1.0\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
      \\textbf{{#1}} & \\textbf{{\\small #2}} \\\\
      \\textit{{\\small#3}} & \\textit{{\\small #4}} \\\\
    \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\newcommand{{\\resumeSubSubheading}}[2]{{
    \\item
    \\begin{{tabular*}}{{0.97\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
      \\textit{{\\small#1}} & \\textit{{\\small #2}} \\\\
    \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\newcommand{{\\resumeProjectHeading}}[2]{{
    \\item
    \\begin{{tabular*}}{{1.001\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
      \\small#1 & \\textbf{{\\small #2}}\\\\
    \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\newcommand{{\\resumeSubItem}}[1]{{\\resumeItem{{#1}}\\vspace{{-4pt}}}}

\\renewcommand\\labelitemi{{$\\vcenter{{\\hbox{{\\small$\\bullet$}}}}$}}
\\renewcommand\\labelitemii{{$\\vcenter{{\\hbox{{\\small$\\bullet$}}}}$}}

\\newcommand{{\\resumeSubHeadingListStart}}{{\\begin{{itemize}}[leftmargin=0.0in, label={{}}]}}
\\newcommand{{\\resumeSubHeadingListEnd}}{{\\end{{itemize}}}}
\\newcommand{{\\resumeItemListStart}}{{\\begin{{itemize}}}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\vspace{{-5pt}}}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\begin{{document}}

\\begin{{center}}
    {{\\Huge \\scshape \\textbf{{{self._escape_latex(personal_info.get('full_name', 'Your Name'))}}}}} \\\\ \\vspace{{8pt}}
    
    \\small {{\\raisebox{{-0.2\\height}} {{{self._escape_latex(personal_info.get('phone', '+1-xxx-xxx-xxxx'))}}}}} $|$ {{\\raisebox{{-0.2\\height}} {{{self._escape_latex(personal_info.get('email', 'email@example.com'))}}}}} $|$ 
    \\href{{{personal_info.get('linkedin', '#')}}}{{\\raisebox{{-0.2\\height}} {{\\underline{{LinkedIn}}}}}} $|$
    \\href{{{personal_info.get('github', '#')}}}{{\\raisebox{{-0.2\\height}} {{\\underline{{GitHub}}}}}} $|$'''
        
        if personal_info.get('leetcode'):
            latex_code += f'''
    \\href{{{personal_info.get('leetcode', '#')}}}{{\\raisebox{{-0.2\\height}} {{\\underline{{LeetCode}}}}}} $|$'''
            
        if personal_info.get('portfolio'):
            latex_code += f'''
    \\href{{{personal_info.get('portfolio', '#')}}}{{\\raisebox{{-0.2\\height}} {{\\underline{{Portfolio}}}}}}'''
        
        latex_code += f'''

    \\vspace{{-8pt}}
\\end{{center}}
\\vspace{{-2pt}}

%-----------EDUCATION-----------
\\section{{Education}}
\\vspace{{-0pt}}
\\begin{{itemize}}[leftmargin=0in, label={{}}]
\\item
{{\\textbf{{{self._escape_latex(education.get('university', 'University Name'))}}} \\hfill \\textbf {{{self._escape_latex(education.get('graduation_date', 'Expected May 2026'))}}}}} \\\\
{{{self._escape_latex(education.get('degree', 'Bachelor of Technology'))}}} \\\\
{{{self._escape_latex(education.get('major', 'Major in Computer Science'))}}} \\\\
\\end{{itemize}}
\\vspace{{-15pt}}

%----------- TECHNICAL SKILLS -----------
\\section{{Technical Skills}}
    \\begin{{itemize}}[leftmargin=0in, label={{}}]
    \\small{{\\item{{'''
        
        skill_categories = [
            ('Programming Languages', skills.get('programming_languages', 'Python, JavaScript')),
            ('Data Analysis & Visualization Libraries', skills.get('data_libraries', 'pandas, NumPy, Matplotlib')),
            ('Tools & Platforms', skills.get('tools_platforms', 'Excel, Power BI, Tableau')),
            ('Core Data Skills', skills.get('core_skills', 'Data Analysis, Machine Learning')),
            ('Soft Skills', skills.get('soft_skills', 'Analytical Reasoning, Communication'))
        ]
        
        skill_lines = []
        for category, skill_list in skill_categories:
            if skill_list and skill_list.strip():
                skill_lines.append(f'     \\textbf{{{category}}}{{: {{{self._escape_latex(skill_list)}}}}}')
        
        latex_code += ' \\\\\n     \\vspace{3pt}\n'.join(skill_lines)
        
        latex_code += f'''
}}
    \\end{{itemize}}
    \\vspace{{-15pt}}

%-----------PROJECTS-----------
\\section{{Personal Projects}}
    \\vspace{{-5pt}}
    \\resumeSubHeadingListStart'''
    
        for project in projects:
            github_link = f" $|$ \\href{{{project.get('github_link', '#')}}}{{\\underline{{GitHub}}}}" if project.get('github_link') else ""
            latex_code += f'''
    \\resumeProjectHeading
          {{\\textbf{{{self._escape_latex(project.get('name', 'Project Name'))}}} $|$ {self._escape_latex(project.get('technologies', 'Technologies'))}{github_link}}}{{{self._escape_latex(project.get('date', 'Date'))}}}
          \\resumeItemListStart'''
          
            for bullet in project.get('description', []):
                if bullet and bullet.strip():
                    latex_code += f'''
            \\resumeItem{{{self._escape_latex(bullet)}}}'''
                
            latex_code += '''
          \\resumeItemListEnd 
          \\vspace{{-15pt}}'''
    
        latex_code += f'''
    \\resumeSubHeadingListEnd

%-----------EXPERIENCE-----------
\\section{{Internships}}
 \\vspace{{-0pt}}
\\begin{{itemize}}[leftmargin=0in, label={{}}]'''

        for internship in internships:
            cert_link = f" $|$ \\href{{{internship.get('certificate_link', '#')}}}{{\\underline{{Certificate}}}}" if internship.get('certificate_link') else ""
            latex_code += f'''
    \\item
    {{\\textbf{{{self._escape_latex(internship.get('company', 'Company Name'))}}}{cert_link} \\hfill \\textbf {{{self._escape_latex(internship.get('location', 'Location'))}}}}} \\\\
    {{{self._escape_latex(internship.get('position', 'Position Title'))}}} \\hfill \\textbf {{{self._escape_latex(internship.get('dates', 'Start Date - End Date'))}}}}}
     \\vspace{{-5pt}} 
     {{\\small
    \\begin{{itemize}}[leftmargin=0.3in, label=$\\bullet$]'''
    
            for bullet in internship.get('description', []):
                if bullet and bullet.strip():
                    latex_code += f'''
        \\item {self._escape_latex(bullet)}'''
                
            latex_code += '''
    \\end{itemize}
    }'''

        latex_code += f'''
\\end{{itemize}}
\\vspace{{-15pt}}

%-----------COURSEWORK AND ACHIEVEMENTS-----------
\\section{{Achievements and Certifications}}
\\vspace{{-0pt}}
\\begin{{itemize}}[leftmargin=0in, label={{}}]'''

        for achievement in achievements:
            org_link = f" $|$ \\href{{{achievement.get('link', '#')}}}{{\\underline{{{self._escape_latex(achievement.get('issuer', 'Organization'))}}}}}" if achievement.get('link') else f" $|$ {self._escape_latex(achievement.get('issuer', 'Organization'))}"
            latex_code += f'''
     \\item
    {{\\textbf{{{self._escape_latex(achievement.get('name', 'Achievement Name'))}}}{org_link} \\hfill \\textbf {{{self._escape_latex(achievement.get('date', 'Date'))}}}}} \\\\ \\vspace{{-1pt}}'''

        latex_code += '''

\\end{itemize}
\\vspace{-0pt}
\\end{document}'''

        return latex_code

# Template metadata
LATEX_TEMPLATES = {
    "analyst": {
        "name": "Analyst Resume",
        "description": "Custom format matching the user's original resume template",
        "preview_image": "/templates/analyst_preview.png",
        "packages": ["latexsym", "fullpage", "titlesec", "marvosym", "color", "verbatim", "enumitem", "hyperref", "fancyhdr", "babel", "tabularx", "fontawesome5", "multicol", "graphicx", "svg"]
    },
    "modern": {
        "name": "Modern Professional",
        "description": "Clean, modern design with color accents using moderncv package",
        "preview_image": "/templates/modern_preview.png",
        "packages": ["moderncv", "geometry", "inputenc"]
    },
    "academic": {
        "name": "Academic Research", 
        "description": "Traditional academic format for research positions and academia",
        "preview_image": "/templates/academic_preview.png",
        "packages": ["geometry", "enumitem", "hyperref", "xcolor", "titlesec"]
    },
    "classic": {
        "name": "Classic Business",
        "description": "Traditional professional format for business and corporate roles",
        "preview_image": "/templates/classic_preview.png",
        "packages": ["geometry", "enumitem", "hyperref", "titlesec"]
    }
}

COLOR_SCHEMES = {
    "blue": {"name": "Professional Blue", "description": "Classic blue accent color"},
    "green": {"name": "Forest Green", "description": "Natural green accent color"},
    "red": {"name": "Crimson Red", "description": "Bold red accent color"},
    "purple": {"name": "Royal Purple", "description": "Elegant purple accent color"},
    "orange": {"name": "Warm Orange", "description": "Vibrant orange accent color"}
}