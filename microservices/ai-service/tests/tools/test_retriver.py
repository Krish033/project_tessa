from unittest.mock import Mock
from app.pipeline.tools.meta.retriever import ToolRetriever


def test_retrieve_empty_prompt():

    tr = ToolRetriever()
    result = tr.retrieve("", top_k=5)
    assert result == []
    

def test_retrieve():
    retriever = ToolRetriever()

    retriever.embedder._embed_sync = Mock(
        return_value=[0.1, 0.2, 0.3]
    )

    retriever._retrieve_sync = Mock(
        return_value=[
            {"tool_name": "calculator"}
        ]
    )

    result = retriever.retrieve("calculate 10 + 20")

    assert result == [
        {"tool_name": "calculator"}
    ]

    # embedder is called with the prompt
    retriever.embedder._embed_sync.assert_called_once_with(
        "calculate 10 + 20"
    )

    # make sure the retrive sync is called with prompt and top_K
    retriever._retrieve_sync.assert_called_once_with(
        [0.1, 0.2, 0.3],
        "calculate 10 + 20",
        10
    )
