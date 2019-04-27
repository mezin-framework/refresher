from academic_parser import AcademicApi
import mechanize
from bs4 import BeautifulSoup
import urllib2
import cookielib


class UfcgApi(AcademicApi):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.status = ''
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        cj = cookielib.CookieJar()
        self.br.set_cookiejar(cj)

    def authenticate(self):
        if self._login():
            self.status = 'success'
            return True
        else:
            self.status = 'login error'
            return False

    def _login(self):
        self.br.open("https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/")
        self.br.select_form(nr=0)
        self.br.form['login'] = self.username
        self.br.form['senha'] = self.password
        self.br.submit()
        page = self.br.response().read()
        soap = BeautifulSoup(page, 'html.parser')
        a = soap.find('p', class_="lead")
        return a is None

    def logout(self):
        self.br.open('https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=SairDoSistema')

    def get_marks(self):
        if self.status == 'success':
            subjects = self.get_subjects()

            for subject in subjects:
                subject['marks'] = self.get_marks_from_subject(subject)
                subject['absences'] = self.get_absences_from_subject(subject)

            self._set_credits(subjects)
        return subjects
    
    def get_subjects(self):
        self.br.open('https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoTurmasListar')
        html =  self.br.response().read()
        soup = BeautifulSoup(html, 'html.parser')
        raw_trs = soup.find_all('tr')
        subjects = []
        for i in range(1, len(raw_trs)):
            tr = raw_trs[i]
            tds = tr.find_all('td')
            semester = tds[0].getText()
            code = tds[1].getText()
            name = tds[2].find('a').getText().strip()
            klass = tds[3].getText()
            subjects.append({"name": name, "class": klass, "code": code, "semester": semester})
        return subjects

    def get_marks_from_subject(self, subject):
        code = subject.get('code')
        class_ = subject.get('class')
        semester = subject.get('semester')
        link = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoTurmaNotas&codigo={}&turma={}&periodo={}".format(code, class_, semester)
        self.br.open(link)
        soup = BeautifulSoup(self.br.response().read(), 'html.parser')
        raw_marks = soup.find_all('td')
        this_marks = []
        for i in range(3, len(raw_marks)-4):
            mark = raw_marks[i]
            this_marks.append(float(mark.getText())) if mark.getText() else this_marks.append("S/N")
        return this_marks
    
    def get_absences_from_subject(self, subject):
        code = subject.get('code')
        class_ = subject.get('class')
        semester = subject.get('semester')
        link = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoTurmaFrequencia&codigo={}&turma={}&periodo={}".format(code, class_, semester)
        self.br.open(link)
        soup = BeautifulSoup(self.br.response().read(), 'html.parser')
        absences = soup.find_all('td')
        absences = int(absences[-2].getText())
        return absences

    def _set_credits(self, subjects):
        self.br.open("https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoHistorico")
        html = self.br.response().read()
        soup = BeautifulSoup(html, 'html.parser')
        trs = soup.find_all('tr')
        trs = trs[1:]
        for subject in subjects:
            for tr in trs:
                tds = tr.find_all('td')
                if tds[1].getText() == subject['name']:
                    subject['credits'] = int(tds[3].getText())
                    break

    def get_credits(self, subjects):
        self.br.open("https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoHistorico")
        html = self.br.response().read()
        soup = BeautifulSoup(html, 'html.parser')
        trs = soup.find_all('tr')
        trs = trs[1:]
        credits = []
        for subject in subjects:
            for tr in trs:
                tds = tr.find_all('td')
                if tds[1].getText() == subject:
                    credits.append(int(tds[3].getText()))
                    break
        return credits

    def get_user_info(self):
        user_info = {}
        if self.status == 'success':
            self.br.open("https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoHistorico")
            html = self.br.response().read()
            soup = BeautifulSoup(html, 'html.parser')

            semesters = soup.find(id="periodos-integralizados")
            semesters = semesters.find_all('div')
            total_semesters = semesters[1].getText()
            max_semesters = semesters[5].getText()

            cra = soup.find(id="integralizacao")
            cra = cra.find(class_="panel-body")
            cra = cra.find(class_="row")
            cra = cra.find_all("div")
            cra = cra[1].get_text()

            total_subjects = soup.find(id="integralizacao")
            total_subjects = total_subjects.find(class_="table")
            total_subjects = total_subjects.find("tbody")
            total_subjects = total_subjects.find_all("tr")
            total_subjects = total_subjects[6]
            total_subjects = total_subjects.find_all("td")[5]
            total_subjects = total_subjects.getText()

            user_info['semesters'] = int(total_semesters)
            user_info['max_semesters'] = int(max_semesters)
            user_info['cra'] = float(cra.replace(',','.'))
            user_info['total_subjects'] = "".join([x.strip() for x in total_subjects.split()])

        return user_info
