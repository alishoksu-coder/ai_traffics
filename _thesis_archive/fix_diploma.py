import win32com.client
import os

word = win32com.client.Dispatch("Word.Application")
word.Visible = False

doc_path = os.path.abspath("Suleimenov_Alisher_VTIPO-45_REPORT_GOST.docx")
doc = word.Documents.Open(doc_path)

def replace_text(find_text, replace_text_val, match_case=False):
    find = word.Selection.Find
    word.Selection.HomeKey(Unit=6) # wdStory
    find.ClearFormatting()
    find.Replacement.ClearFormatting()
    find.Text = find_text
    find.Replacement.Text = replace_text_val
    find.Forward = True
    find.Wrap = 1 # wdFindContinue
    find.Format = False
    find.MatchCase = match_case
    find.MatchWholeWord = False
    find.MatchWildcards = False
    find.MatchSoundsLike = False
    find.MatchAllWordForms = False
    find.Execute(Replace=2) # wdReplaceAll

replacements = {
    "algorithmderge neg_zdegen": "алгоритмдерге негізделген",
    "baskars": "басқару",
    "automatics in thailand": "автоматты басқару",
    "derekterge negіzdelіp": "деректерге негізделіп",
    "bagdarsham phasalyn": "бағдаршам фазаларын",
    "Vaze": "Waze",
    "краудсорсинг директорлары": "краудсорсинг деректері",
    "Бейімделгіш қаптар үшін baskars — пайдалану нұсқаулары деректерге негізделіп, bagdarsham phasalyn automatics in thailand": "Бейімделгіш басқару жүйелері нақты уақыттағы деректерге негізделіп, бағдаршам фазаларын автоматты түрде оңтайландырады",
    "Zhasanda Intelligence (ЖИ) әйелдердің ішек шаншуы мәселесіне": "Жасанды интеллект (ЖИ) көлік ағындарын басқару және болжау процесін автоматтандыруға мүмкіндік береді",
    "колик": "көлік",
    "жуйесi": "жүйесі",
    "корингендей": "көрінгендей",
    "бiздiн": "біздің",
    "усынылатын": "ұсынылатын",
    "Google Maps - Ұлыбританияда кеңінен қолданылатын": "Google Maps — әлемде кеңінен қолданылатын",
    "Бұл кемшілік Орталық Азиядағы оның негізгі кемшілігі болып табылады.": "Оның кемшілігі — кейбір аймақтарда пайдаланушылар саны шектеулі болуы мүмкін.",
    "2-кесте^pНавигация жүйелерді  салыстырмалы талдау^p2-кесте^pНавигация жүйелерді  салыстырмалы талдау": "2-кесте^pНавигация жүйелерді  салыстырмалы талдау",
    "Қосынды": "Σ",
    "LSTM жүйеде орнатылмаған, бірақ ақпаратты сақтау үшін қолданылады": "LSTM болашақта енгізу үшін қарастырылады",
    "README-де": "Жобада",
    "репозиторийде": "Жобада",
    "Репозиторий": "Жоба",
    "Біздің ең үлкен компоненттеріміз": "Жүйенің негізгі компоненттері",
    "біздің ең үлкен компоненттеріміз": "Жүйенің негізгі компоненттері",
    "Artificial Intelligence": "ЖИ",
    "Zhasanda Intelligence": "ЖИ",
    "жасанды интеллект (ЖИ)": "Жасанды интеллект (AI)",
    "Жасанды Интеллект  көмегімен автоматтандырылған": "ЖИ көмегімен автоматтандырылған",
}

for f, r in replacements.items():
    replace_text(f, r)

# Replace novelty paragraph
word.Selection.HomeKey(Unit=6)
find = word.Selection.Find
find.ClearFormatting()
find.Text = "Ғылыми инновация: «Көліктегі ЖИ»"
find.Forward = True
find.Wrap = 1
if find.Execute():
    word.Selection.Expand(4) # Expand to paragraph
    novelty_new = "Ғылыми жаңалығы:\n– SMA, EMA және Random Forest негізіндегі гибридті модель;\n– Z-score және rule-based әдістер арқылы аномалияларды анықтау;\n– ауа райы факторларын ескеретін болжам жүйесі;\n– нақты уақыттағы көпдеңгейлі архитектура.\nГибридті модельдерді қолдану болжау дәлдігін арттырады.\n"
    word.Selection.Text = novelty_new

# Save and close
out_path = os.path.abspath("Suleimenov_Alisher_VTIPO-45_REPORT_GOST_fixed.docx")
doc.SaveAs(out_path)
doc.Close()
word.Quit()
print("Replacements completed successfully.")
