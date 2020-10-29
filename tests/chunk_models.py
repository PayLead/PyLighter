import pytest

from chunk_models import Chunk, Chunks


@pytest.mark.parametrize(
    "labels, expected",
    [
        (["O", "O", "B-Loc", "I-Loc"], [(2, 3)]),
        (["O", "O", "B-Loc", "B-Loc"], [(2, 2), (3, 3)]),
        (["B-Loc", "B-Loc", "O", "B-Loc"], [(0, 0), (1, 1), (3, 3)]),
        (["B-Loc", "I-Loc", "O", "B-Loc"], [(0, 1), (3, 3)]),
        (["B-Loc", "I-Loc", "O", "O"], [(0, 1)]),
    ],
)
def test_labels_to_chunks(labels, expected):
    chunks = Chunks(labels=labels)

    assert len(chunks.chunks) == len(expected)

    chunks_indices = []
    for chunk in chunks.chunks:
        assert (chunk.start_index, chunk.end_index) in expected
        chunks_indices.append((chunk.start_index, chunk.end_index))

    chunks_indices.sort()
    assert chunks_indices == expected


@pytest.mark.parametrize(
    "labels, new_chunk, expected",
    [
        (
            ["O", "O", "B-Loc", "I-Loc"],
            Chunk(start_index=0, end_index=1, label="Loc"),
            [(0, 1), (2, 3)],
        ),
        (
            ["O", "O", "B-Loc", "B-Loc"],
            Chunk(start_index=0, end_index=1, label="Loc"),
            [(0, 1), (2, 2), (3, 3)],
        ),
        (
            ["B-Loc", "B-Loc", "O", "B-Loc"],
            Chunk(start_index=0, end_index=1, label="Loc"),
            [(0, 1), (3, 3)],
        ),
        (
            ["B-Loc", "B-Loc", "I-Loc", "B-Loc"],
            Chunk(start_index=0, end_index=1, label="Loc"),
            [(0, 1), (2, 2), (3, 3)],
        ),
        (
            ["B-Loc", "O", "B-Loc", "I-Loc"],
            Chunk(start_index=1, end_index=2, label="Loc"),
            [(0, 0), (1, 2), (3, 3)],
        ),
        (
            ["B-Loc", "I-Loc", "O", "B-Loc"],
            Chunk(start_index=0, end_index=1, label="Loc"),
            [(0, 1), (3, 3)],
        ),
        (
            ["B-Loc", "I-Loc", "O", "O"],
            Chunk(start_index=0, end_index=1, label="Loc"),
            [(0, 1)],
        ),
        (
            ["B-Loc", "O", "O", "O"],
            Chunk(start_index=0, end_index=1, label="Loc"),
            [(0, 1)],
        ),
        (
            ["B-Loc", "I-Loc", "I-Loc", "I-Loc"],
            Chunk(start_index=1, end_index=2, label="Loc"),
            [(0, 0), (1, 2), (3, 3)],
        ),
    ],
)
def test_add_new_chunk_and_update(labels, new_chunk, expected):
    chunks = Chunks(labels=labels)
    chunks.add_new_chunk_and_update(new_chunk)

    assert len(chunks.chunks) == len(expected)

    chunks_indices = []
    for chunk in chunks.chunks:
        assert (chunk.start_index, chunk.end_index) in expected
        chunks_indices.append((chunk.start_index, chunk.end_index))

    chunks_indices.sort()
    assert chunks_indices == expected


@pytest.mark.parametrize(
    "labels",
    [
        ["O", "O", "B-Loc", "I-Loc"],
        ["O", "O", "B-Loc", "B-Loc"],
        ["B-Loc", "B-Loc", "O", "B-Loc"],
        ["B-Loc", "I-Loc", "O", "O"],
        ["B-Loc", "O", "O", "O"],
        ["B-Loc", "I-Loc", "I-Loc", "I-Loc"],
    ],
)
def test_chunks_to_labels(labels):
    chunks = Chunks(labels=labels)

    label_output = chunks.to_labels()

    assert labels == label_output


# @pytest.mark.parametrize(
#     "labels",
#     [
#         ["O", "O", "B-Loc", "I-Loc"],
#         ["O", "O", "B-Loc", "B-Loc"],
#         ["B-Loc", "B-Loc", "O", "B-Loc"],
#         ["B-Loc", "I-Loc", "O", "O"],
#         ["B-Loc", "O", "O", "O"],
#         ["B-Loc", "I-Loc", "I-Loc", "I-Loc"],
#     ],
# )
# def test_remove_chunks(labels, idx_chunks_to_remove, expected):
#     # TODO O(m*n) improve
#     for chunk in chunks_to_remove[::-1]:
#         self.remove_chunk_by_id(chunk.id)
