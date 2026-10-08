from copy import deepcopy
import time
from pathlib import Path
from streamlit.testing.v1 import AppTest
from core.leitner import initial, key
from core.trainer import Session
from data.vocabulary import builtin_lists
from services.database import ServiceError

APP = str(Path(__file__).parents[1] / 'glostranare_web-v4.py')


def app(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'app.sqlite3'))
    monkeypatch.setenv('BACKEND','sqlite')
    monkeypatch.setenv('ADMIN_PASSWORD','a-long-test-password')
    at = AppTest.from_file(APP, default_timeout=10).run()
    next(s for s in at.selectbox if s.label == 'Välj kurs').set_value('Spanska fortsättning').run()
    return at


def click(at,label):
    return next(b for b in at.button if b.label == label).click().run()


def guest(at):
    click(at,'Öppna listan')
    click(at,'▶ Öva på dessa glosor')
    return at


def test_guest_quiz_switch_lists_and_direction_preserve_progress(tmp_path,monkeypatch):
    at = guest(app(tmp_path,monkeypatch))
    assert not at.code  # HTML branding must render, not become an indented Markdown code block.
    click(at,'▶ Fortsätt träna')
    vocab = next(v for v in builtin_lists() if v['id'] == at.session_state.list_id)
    word = next(w for w in vocab['words'] if w['id'] == at.session_state.session.current)
    next(r for r in at.radio if r.label == 'Välj översättning').set_value(word['accepted_answers'][0]).run()
    click(at,'Kontrollera svar')
    assert not at.exception
    saved = deepcopy(at.session_state.progress)
    assert len(saved) == 1
    at.run()
    assert at.session_state.progress == saved  # no double scoring on rerun
    click(at,'← Alla gloslistor')
    click(at,'Öppna listan')
    assert at.session_state.progress == saved
    at.sidebar.selectbox[0].set_value('Målspråk till svenska').run()
    assert at.session_state.progress == saved
    assert at.session_state.session is None


def test_write_near_answer_and_hint_do_not_promote(tmp_path,monkeypatch):
    at = guest(app(tmp_path,monkeypatch))
    vocab = next(v for v in builtin_lists() if any(w['accepted_answers'][0] == 'miércoles' for w in v['words']))
    word = next(w for w in vocab['words'] if w['accepted_answers'][0] == 'miércoles')
    at.session_state.list_id = vocab['id']
    at.session_state.session = Session([word['id']],mode='write')
    at.run()
    next(t for t in at.text_input if t.label.startswith('Skriv på')).set_value('miercoles')
    click(at,'Rätta mitt svar')
    assert at.session_state.session.feedback['result'] == 'near'
    assert at.session_state.progress[key(vocab['id'],word['id'],'forward')]['box'] == 1
    at.session_state.session = Session([word['id']],mode='write')
    at.session_state.progress = {}
    at.run()
    click(at,'💡 En bokstav')
    next(t for t in at.text_input if t.label.startswith('Skriv på')).set_value('miércoles')
    click(at,'Rätta mitt svar')
    assert at.session_state.progress[key(vocab['id'],word['id'],'forward')]['box'] == 1
    assert not at.exception


def test_network_failure_keeps_response_and_blocks_next(tmp_path,monkeypatch):
    at = guest(app(tmp_path,monkeypatch))
    from services.database import LocalDatabase
    def fail(*args,**kwargs):
        raise ServiceError('Tillfälligt sparfel')
    monkeypatch.setattr(LocalDatabase,'save_progress',fail)
    at.session_state.user = {'name':'Test','role':'student','token':'fake'}
    click(at,'▶ Fortsätt träna')
    vocab = next(v for v in builtin_lists() if v['id'] == at.session_state.list_id)
    word = next(w for w in vocab['words'] if w['id'] == at.session_state.session.current)
    next(r for r in at.radio if r.label == 'Välj översättning').set_value(word['accepted_answers'][0])
    click(at,'Kontrollera svar')
    assert at.session_state.pending is not None
    assert next(b for b in at.button if b.label == 'Nästa ord →').disabled
    snapshot = deepcopy(at.session_state.progress)
    monkeypatch.setattr(LocalDatabase,'save_progress',lambda *args,**kwargs:1)
    click(at,'Försök spara igen')
    assert at.session_state.pending is None and at.session_state.progress == snapshot
    assert not at.exception


def test_teacher_panel_can_create_user_and_list(tmp_path,monkeypatch):
    at = app(tmp_path,monkeypatch)
    click(at,'Logga in')
    next(t for t in at.text_input if t.label == 'Lärarlösenord').set_value('a-long-test-password')
    click(at,'Öppna lärarpanelen')
    assert not at.exception
    next(t for t in at.text_input if t.label == 'Elevens namn').set_value('Test')
    next(t for t in at.text_input if t.label == 'Klass').set_value('2A')
    next(t for t in at.text_input if t.label.startswith('Ny PIN-kod')).set_value('0123')
    click(at,'Skapa konto')
    assert not at.exception
    next(t for t in at.text_input if t.label == 'Listans namn').set_value('Ny lista')
    at.text_area[0].set_value('hund\tperro\nkatt\tgato')
    click(at,'Spara ny lista')
    assert len(at.session_state.lists) == 9 and not at.exception


def test_expired_login_can_save_pending_answer_without_reset(tmp_path,monkeypatch):
    from services.database import LocalDatabase
    at = app(tmp_path,monkeypatch)
    db = LocalDatabase(tmp_path/'app.sqlite3','a-long-test-password')
    teacher = db.teacher_login('a-long-test-password')['token']
    db.create_user(teacher,'Test','2A','0123')
    user = db.authenticate('Test','2A','0123')
    at.session_state.user = user
    at.run()
    click(at,'Öppna listan')
    click(at,'▶ Öva på dessa glosor')
    click(at,'▶ Fortsätt träna')
    vocab = next(v for v in builtin_lists() if v['id'] == at.session_state.list_id)
    word = next(w for w in vocab['words'] if w['id'] == at.session_state.session.current)
    db.logout(user['token'])
    next(r for r in at.radio if r.label == 'Välj översättning').set_value(word['accepted_answers'][0])
    click(at,'Kontrollera svar')
    assert at.session_state.save_error[0] == 'auth'
    snapshot = deepcopy(at.session_state.progress)
    next(t for t in at.text_input if t.label == 'PIN-kod igen').set_value('0123')
    click(at,'Logga in och spara svaret')
    assert at.session_state.pending is None and at.session_state.progress == snapshot
    assert db.load_progress(at.session_state.user['token'])['progress'] == snapshot
    assert not at.exception


def test_direct_link_opens_custom_list_without_login_and_survives_rename(tmp_path,monkeypatch):
    from services.database import LocalDatabase
    at = app(tmp_path,monkeypatch)
    db = LocalDatabase(tmp_path/'app.sqlite3','a-long-test-password')
    token = db.teacher_login('a-long-test-password')['token']
    vocab = deepcopy(builtin_lists()[0])
    vocab.update(id='custom_shared',name='Min delbara lista')
    db.save_lists(token,[vocab])
    at = AppTest.from_file(APP,default_timeout=10)
    at.query_params['lista'] = vocab['id']
    at.run()
    assert at.session_state.user['role'] == 'guest'
    assert not any(t.label == 'PIN-kod' for t in at.text_input)
    assert any(s.value == 'Min delbara lista' for s in at.subheader)
    assert at.code[0].value.endswith('?lista=custom_shared')
    click(at,'▶ Öva på dessa glosor')
    click(at,'▶ Fortsätt träna')
    assert at.session_state.session is not None and not at.exception
    vocab['name'] = 'Nytt namn, samma länk'
    db.save_lists(token,[vocab])
    second = AppTest.from_file(APP,default_timeout=10)
    second.query_params['lista'] = vocab['id']
    second.run()
    assert any(s.value == vocab['name'] for s in second.subheader)


def test_invalid_link_and_return_to_library_clear_query(tmp_path,monkeypatch):
    at = app(tmp_path,monkeypatch)
    at.query_params['lista'] = 'missing-id'
    at.run()
    assert any('finns inte' in w.value for w in at.warning)
    click(at,'Visa alla gloslistor')
    assert 'lista' not in at.query_params and at.session_state.list_id is None
    click(at,'Öppna listan')
    assert at.query_params['lista'] == [at.session_state.list_id]
    click(at,'← Alla gloslistor')
    assert 'lista' not in at.query_params and not at.exception


def test_optional_login_keeps_list_and_loads_account_without_mixing_guest_progress(tmp_path,monkeypatch):
    from services.database import LocalDatabase
    at = guest(app(tmp_path,monkeypatch))
    list_id = at.session_state.list_id
    db = LocalDatabase(tmp_path/'app.sqlite3','a-long-test-password')
    token = db.teacher_login('a-long-test-password')['token']
    db.create_user(token,'Test','2A','0123')
    user = db.authenticate('Test','2A','0123')
    saved = {'stored-word':initial()}
    db.save_progress(user['token'],saved,0,'test-login')
    at.session_state.progress = {'guest-word':initial()}
    click(at,'Logga in')
    assert not any(t.label == 'Klass' for t in at.text_input)
    next(t for t in at.text_input if t.label == 'Namn').set_value('Test')
    next(t for t in at.text_input if t.label == 'PIN-kod').set_value('0123')
    click(at,'Logga in')
    assert at.session_state.list_id == list_id
    assert at.session_state.progress == saved
    assert at.session_state.user['role'] == 'student'
    assert not at.exception
    click(at,'Logga ut')
    assert at.session_state.user['role'] == 'guest'
    assert at.session_state.progress == {} and at.session_state.list_id == list_id


def test_listening_to_answer_prevents_promotion(tmp_path,monkeypatch):
    at = guest(app(tmp_path,monkeypatch))
    click(at,'▶ Fortsätt träna')
    vocab = next(v for v in builtin_lists() if v['id'] == at.session_state.list_id)
    word = next(w for w in vocab['words'] if w['id'] == at.session_state.session.current)
    click(at,'🔊 Lyssna på svaret som hjälp')
    next(r for r in at.radio if r.label == 'Välj översättning').set_value(word['accepted_answers'][0])
    click(at,'Kontrollera svar')
    assert at.session_state.session.feedback['assisted']
    assert at.session_state.progress[key(vocab['id'],word['id'],'forward')]['box'] == 1
    assert not at.exception


def test_feedback_is_rendered_before_remote_save(tmp_path,monkeypatch):
    import streamlit as st
    from services.database import LocalDatabase
    at = guest(app(tmp_path,monkeypatch))
    at.session_state.user = {'name':'Test','role':'student','token':'fake'}
    events = []
    success = st.success
    def show_success(body,*args,**kwargs):
        if str(body).startswith('Rätt!'):
            events.append('feedback')
        return success(body,*args,**kwargs)
    monkeypatch.setattr(st,'success',show_success)
    def remote_save(*args,**kwargs):
        assert 'feedback' in events
        events.append('save')
        return 1
    monkeypatch.setattr(LocalDatabase,'save_progress',remote_save)
    click(at,'▶ Fortsätt träna')
    vocab = next(v for v in builtin_lists() if v['id'] == at.session_state.list_id)
    word = next(w for w in vocab['words'] if w['id'] == at.session_state.session.current)
    next(r for r in at.radio if r.label == 'Välj översättning').set_value(word['accepted_answers'][0])
    click(at,'Kontrollera svar')
    assert events.index('feedback') < events.index('save')
    assert events.count('save') == 1
    assert at.session_state.pending is None
    assert at.session_state.session.answered == 1
    assert not at.exception


def test_course_is_required_first_and_kept_when_returning(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'course.sqlite3'))
    monkeypatch.setenv('BACKEND', 'sqlite')
    at = AppTest.from_file(APP).run()
    course = next(s for s in at.selectbox if s.label == 'Välj kurs')
    assert course.value is None and not any(b.label == 'Öppna listan' for b in at.button)
    course.set_value('Spanska nybörjare').run()
    click(at, 'Öppna listan')
    click(at, '← Alla gloslistor')
    assert next(s for s in at.selectbox if s.label == 'Välj kurs').value == 'Spanska nybörjare'
    assert any(b.label == 'Öppna listan' for b in at.button) and not at.exception


def test_teacher_creates_ab_pdfs_and_hides_old_results_after_option_change(tmp_path, monkeypatch):
    at = app(tmp_path, monkeypatch)
    click(at, 'Logga in')
    next(t for t in at.text_input if t.label == 'Lärarlösenord').set_value('a-long-test-password')
    click(at, 'Öppna lärarpanelen')
    next(c for c in at.checkbox if c.label == 'Skapa A- och B-version').check().run()
    click(at, 'Skapa PDF')
    assert at.session_state.print_result[1].startswith(b'%PDF')
    assert at.session_state.print_result[2].startswith(b'%PDF')
    assert any('Förhöret och facit är klara' in s.value for s in at.success)
    next(r for r in at.radio if r.label == 'Språkriktning för förhöret').set_value('reverse').run()
    assert not any('Förhöret och facit är klara' in s.value for s in at.success)
    assert not at.exception


def test_live_progress_shows_whole_list_updates_once_and_follows_direction(tmp_path, monkeypatch):
    at = guest(app(tmp_path, monkeypatch))
    vocab = next(v for v in builtin_lists() if v['id'] == at.session_state.list_id)
    def row():
        return next(m.value for m in at.markdown if 'class="practice-progress"' in m.value)
    click(at, '▶ Fortsätt träna')
    total = len(vocab['words'])
    assert f'Ska övas <b>{total}</b>' in row()
    assert 'På väg <b>0</b>' in row() and 'Kan bra <b>0</b>' in row()
    word = next(w for w in vocab['words'] if w['id'] == at.session_state.session.current)
    next(r for r in at.radio if r.label == 'Välj översättning').set_value(word['accepted_answers'][0])
    click(at, 'Kontrollera svar')
    assert f'Ska övas <b>{total-1}</b>' in row() and 'På väg <b>1</b>' in row()
    assert at.session_state.session.answered == 1
    at.run()
    assert 'På väg <b>1</b>' in row() and at.session_state.session.answered == 1
    at.sidebar.selectbox[0].set_value('Målspråk till svenska').run()
    click(at, '▶ Fortsätt träna')
    assert f'Ska övas <b>{total}</b>' in row() and 'På väg <b>0</b>' in row()
    assert '→ svenska' in row() and not at.exception


def test_live_progress_preserves_green_on_help_and_moves_wrong_answer_back(tmp_path, monkeypatch):
    at = guest(app(tmp_path, monkeypatch))
    vocab = next(v for v in builtin_lists() if v['id'] == at.session_state.list_id)
    word = vocab['words'][0]
    state = {**initial(), 'box': 3, 'next_review': 0}
    at.session_state.progress = {key(vocab['id'], word['id'], 'forward'):state}
    at.session_state.session = Session([word['id']], mode='write')
    at.run()
    click(at, '💡 En bokstav')
    next(t for t in at.text_input if t.label.startswith('Skriv på')).set_value(word['accepted_answers'][0])
    click(at, 'Rätta mitt svar')
    markup = next(m.value for m in at.markdown if 'class="practice-progress"' in m.value)
    assert 'Kan bra <b>1</b>' in markup
    at.session_state.session = Session([word['id']], mode='write')
    at.run()
    next(t for t in at.text_input if t.label.startswith('Skriv på')).set_value('xxxxxx')
    click(at, 'Rätta mitt svar')
    markup = next(m.value for m in at.markdown if 'class="practice-progress"' in m.value)
    # Ett fel svar flyttar ett grönt ord ett steg ner, till På väg.
    assert 'Kan bra <b>0</b>' in markup and 'På väg <b>1</b>' in markup
    assert f"Ska övas <b>{len(vocab['words']) - 1}</b>" in markup and not at.exception
