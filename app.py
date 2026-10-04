from __future__ import annotations
from pathlib import Path
import streamlit as st

from src.config import *
from src.documents import prepare_chunks, sha256_bytes
from src.ollama_client import check_connection, model_available, list_models, pull_model
from src.store import LocalKnowledgeStore
from src.rag import answer_question

st.set_page_config(page_title='Local Document Intelligence', page_icon='📚', layout='wide')
st.title('📚 Local Document Intelligence')
st.caption('Upload → Index → Ask. Everything stays local when Ollama is local.')

with st.sidebar:
    st.header('1. Local setup')
    host = st.text_input('Ollama URL', DEFAULT_OLLAMA_HOST)

    # Discover installed models so the UI never assumes a model that is not present.
    try:
        installed_models = list_models(host)
    except Exception:
        installed_models = []

    chat_candidates = [m for m in installed_models if 'embed' not in m.lower()]
    embed_candidates = [m for m in installed_models if 'embed' in m.lower()]

    saved_chat = st.session_state.get('chat_model', DEFAULT_CHAT_MODEL)
    saved_embed = st.session_state.get('embed_model', DEFAULT_EMBED_MODEL)

    if chat_candidates:
        chat_default = saved_chat if saved_chat in chat_candidates else chat_candidates[0]
        chat_model = st.selectbox('Chat model', chat_candidates, index=chat_candidates.index(chat_default), key='chat_model')
    else:
        chat_model = st.text_input('Chat model', saved_chat, key='chat_model_text')

    if embed_candidates:
        embed_default = saved_embed if saved_embed in embed_candidates else embed_candidates[0]
        embed_model = st.selectbox('Embedding model', embed_candidates, index=embed_candidates.index(embed_default), key='embed_model')
    else:
        embed_model = st.text_input('Embedding model', saved_embed, key='embed_model_text')

    if st.button('Refresh Ollama models', use_container_width=True):
        st.rerun()

    with st.expander('Install a model from Ollama'):
        pull_name = st.text_input('Model name', placeholder='e.g. llama3.2 or nomic-embed-text')
        if st.button('Pull / Install model', use_container_width=True):
            if not pull_name.strip():
                st.warning('Enter a model name.')
            else:
                with st.spinner(f'Pulling {pull_name.strip()} from Ollama…'):
                    try:
                        pull_model(host, pull_name.strip())
                        st.success(f'Installed {pull_name.strip()}.')
                        st.rerun()
                    except Exception as exc:
                        st.error(f'Could not pull model: {exc}')

    if installed_models:
        st.caption('Installed: ' + ', '.join(installed_models))
    else:
        st.warning('No Ollama models detected. Install one using the panel above.')

    if st.button('Test Ollama', use_container_width=True):
        ok, msg, models = check_connection(host)
        if ok:
            st.success(msg)
            st.write('Available models:', ', '.join(models) or 'none')
        else:
            st.error(msg)
    st.divider()
    st.header('2. Retrieval settings')
    chunk_size = st.slider('Chunk size', 300, 2000, DEFAULT_CHUNK_SIZE, 100)
    overlap = st.slider('Chunk overlap', 0, min(500, chunk_size - 100), min(DEFAULT_CHUNK_OVERLAP, chunk_size - 100), 20)
    top_k = st.slider('Chunks retrieved', 1, 12, DEFAULT_TOP_K)

try:
    store = LocalKnowledgeStore(host, embed_model)
except Exception as exc:
    st.error(f'Could not open the local database: {exc}')
    st.stop()

sources = store.list_sources()
col1, col2, col3 = st.columns(3)
col1.metric('Indexed documents', len(sources))
col2.metric('Indexed chunks', store.count())
col3.metric('Embedding model', embed_model)

if store.count() > 0:
    st.success(f'Knowledge base ready: {len(sources)} document(s), {store.count()} chunk(s). You can ask questions now.')
else:
    st.info('Knowledge base is empty. Start in **Add Documents** and click **Save and Index**.')

upload_tab, ask_tab, library_tab, setup_tab = st.tabs(['1 · Add Documents', '2 · Ask / Extract Wisdom', '3 · Knowledge Library', 'Setup / Diagnostics'])

with upload_tab:
    st.subheader('Upload and index')
    uploads = st.file_uploader('Choose PDF, Markdown, or TXT files', type=['pdf', 'md', 'txt'], accept_multiple_files=True)
    if uploads:
        st.write('Selected:', ', '.join(x.name for x in uploads))
    if st.button('Save and Index Selected Documents', type='primary', disabled=not uploads, use_container_width=True):
        progress = st.progress(0)
        success, errors = 0, []
        for i, upload in enumerate(uploads):
            try:
                raw = upload.getvalue()
                source_id = sha256_bytes(raw)
                safe_name = Path(upload.name).name
                destination = DOCUMENTS_DIR / f'{source_id[:12]}_{safe_name}'
                destination.write_bytes(raw)
                store.delete_source(source_id)
                chunks = prepare_chunks(destination, source_id, chunk_size, overlap)
                added = store.add_chunks(chunks)
                if added == 0:
                    raise RuntimeError('The file produced zero chunks.')
                success += 1
                st.write(f'✅ {upload.name}: {added} chunks indexed')
            except Exception as exc:
                errors.append(f'{upload.name}: {exc}')
            progress.progress((i + 1) / len(uploads))
        if errors:
            for error in errors:
                st.error(error)
        if success:
            st.success(f'Indexed {success} file(s). The Ask tab is now ready.')
            st.rerun()

with ask_tab:
    st.subheader('Ask your documents')
    if store.count() == 0:
        st.warning('Your library is empty. Upload and index documents in the first tab.')
    else:
        st.success(f'Ready to search {len(sources)} document(s).')
        suggested = st.selectbox('Example question', [
            'Write my own question…',
            'What are the most important lessons across these documents?',
            'What problems recur, and what causes them?',
            'Extract key facts, insights, recommendations, and knowledge gaps.',
            'What do the documents disagree about?',
        ])
        default_question = '' if suggested == 'Write my own question…' else suggested
        with st.form('question_form'):
            question = st.text_area('Your question', value=default_question, height=110)
            submitted = st.form_submit_button('Search Documents and Answer', type='primary', use_container_width=True)
        if submitted:
            if not question.strip():
                st.warning('Enter a question first.')
            elif not model_available(host, chat_model):
                st.error(f'Chat model "{chat_model}" is not installed. Use **Install a model from Ollama** in the sidebar, then click **Refresh Ollama models**.')
            elif not model_available(host, embed_model):
                st.error(f'Embedding model "{embed_model}" is not installed. Use **Install a model from Ollama** in the sidebar, then click **Refresh Ollama models**.')
            else:
                with st.spinner('Searching local evidence and generating a grounded answer…'):
                    try:
                        result = answer_question(host, chat_model, store, question.strip(), top_k)
                        st.markdown('### Answer')
                        st.markdown(result['answer'])
                        if result['sources']:
                            st.markdown('### Retrieved evidence')
                            for n, source in enumerate(result['sources'], 1):
                                loc = f" · page {source['page']}" if source['page'] else ''
                                with st.expander(f"{n}. {source['file_name']}{loc} · distance {source['distance']:.3f}"):
                                    st.write(source['excerpt'])
                    except Exception as exc:
                        st.error(f'Question failed: {exc}')
                        st.exception(exc)

with library_tab:
    st.subheader('Knowledge library')
    if not sources:
        st.info('No indexed documents yet.')
    else:
        for source in sources:
            left, mid, right = st.columns([5, 2, 2])
            left.write(f"**{source['file_name']}**")
            left.caption(f"{source['file_type'].upper()} · {source['source_id'][:12]}")
            mid.write(f"{source['chunks']} chunks")
            if right.button('Remove', key=f"remove_{source['source_id']}"):
                store.delete_source(source['source_id'])
                st.rerun()
        st.divider()
        if st.button('Clear Entire Knowledge Index', type='secondary'):
            store.clear()
            st.success('Knowledge index cleared.')
            st.rerun()

with setup_tab:
    st.subheader('Diagnostics')
    ok, msg, models = check_connection(host)
    if ok:
        st.success(msg)
        st.write('Ollama models:', ', '.join(models) or 'none')
        st.write(f'Chat model available: **{model_available(host, chat_model)}**')
        st.write(f'Embedding model available: **{model_available(host, embed_model)}**')
    else:
        st.error(msg)
    st.write(f'Chroma database: `{CHROMA_DIR}`')
    st.write(f'Document storage: `{DOCUMENTS_DIR}`')
    st.write(f'Collection: `{COLLECTION_NAME}`')
    st.write(f'Indexed chunks: **{store.count()}**')
    st.caption('If you change the embedding model, clear the knowledge index and re-index the documents. Different embedding models can produce incompatible vector dimensions.')
