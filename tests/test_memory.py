def test_memory_crud_session(memory_store):
    session_id = memory_store.create_session("Test Goal", "Test Title")
    sessions = memory_store.list_sessions()
    assert any(s["id"] == session_id for s in sessions)
    
    memory_store.delete_session(session_id)
    sessions = memory_store.list_sessions()
    assert not any(s["id"] == session_id for s in sessions)

def test_memory_messages(memory_store):
    session_id = memory_store.create_session("Test Goal", "Test Title")
    memory_store.add_message(session_id, "user", "Hello")
    messages = memory_store.get_messages(session_id)
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"

def test_memory_notes(memory_store):
    note_id = memory_store.save_note("Physics", "Gravity is a force.", "science")
    notes = memory_store.list_notes()
    assert any(n["id"] == note_id for n in notes)
    
    search_results = memory_store.search_notes("Gravity")
    assert len(search_results) > 0
    assert search_results[0]["id"] == note_id

def test_memory_quiz_results(memory_store):
    quiz_id = memory_store.save_quiz_result("Math", 8, 10)
    history = memory_store.get_quiz_history()
    assert any(q["id"] == quiz_id for q in history)
    assert history[0]["score"] == 8

def test_memory_long_term_retrieval(memory_store):
    memory_store.save_note("Photosynthesis", "Plants make food using sunlight.", "biology")
    context = memory_store.retrieve_relevant_context("teach me about plants and sunlight")
    assert "Photosynthesis" in context
    assert "Plants make food" in context
