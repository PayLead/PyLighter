from datetime import datetime


class Chunk:
    def __init__(self, start_index, end_index, label):
        self.id = str(datetime.now()).replace(" ", "")
        self.display_id = f"id_class_chunk_{self.id}"

        self.start_index = start_index
        self.end_index = end_index
        self.label = label

        self.text_display = None

    def update(self, start_index=None, end_index=None, label=None):
        if start_index is not None:
            self.start_index = start_index

        if end_index is not None:
            self.end_index = end_index

        if label:
            self.label = label

        return self


class Chunks:
    def __init__(
        self,
        labels=None,
        labels_size=None,
    ):
        if not labels_size and not labels:
            raise ValueError("Chunks init need either 'labels_size' or 'labels'.")

        self.chunks = []
        self.labels_size = labels_size

        if labels:
            self.chunks = self.labels_to_chunks(labels)
            self.labels_size = len(labels)

    def add_chunk(self, chunk):
        self.chunks.append(chunk)

    def remove_chunk_by_id(self, chunk_id):
        for index, chunk in enumerate(self.chunks):
            if chunk.id == chunk_id:
                del self.chunks[index]
                return

    # TODO add tests
    def add_new_chunk_and_update(self, new_chunk):
        start_index = new_chunk.start_index
        end_index = new_chunk.end_index

        chunks_to_remove = []
        updated_chunks = []
        chunks_to_add = [new_chunk]
        for chunk in self.chunks:
            # Outer sandwich
            if chunk.start_index >= start_index and chunk.end_index <= end_index:
                chunks_to_remove.append(chunk)

            # Inner sandwich
            if chunk.start_index < start_index and chunk.end_index > end_index:
                right_chunk = Chunk(
                    start_index=end_index + 1,
                    end_index=chunk.end_index,
                    label=chunk.label,
                )
                chunks_to_add.append(right_chunk)
                updated_chunks.append(right_chunk)

                chunk.update(end_index=start_index - 1)
                updated_chunks.append(chunk)

            # Left sandwich
            elif chunk.start_index < start_index and chunk.end_index >= start_index:
                chunk.update(end_index=start_index - 1)
                updated_chunks.append(chunk)

            # Right sandwich
            elif chunk.start_index <= end_index and chunk.end_index > end_index:
                chunk.update(start_index=end_index + 1)
                updated_chunks.append(chunk)

        for chunk in chunks_to_add:
            self.add_chunk(chunk)

        self.remove_chunks(chunks_to_remove)

        return updated_chunks, chunks_to_remove

    def remove_chunks(self, chunks_to_remove):
        # TODO O(m*n) improve
        for chunk in chunks_to_remove[::-1]:
            self.remove_chunk_by_id(chunk.id)

    def labels_to_chunks(self, labels):
        start_index = None
        current_label = None
        chunks = []

        for index, label in enumerate(labels):
            if label[:2] == "B-":  # IOB2 format
                if current_label:
                    chunks.append(
                        Chunk(
                            start_index=start_index,
                            end_index=index - 1,
                            label=current_label,
                        )
                    )

                start_index, current_label = index, label[2:]

            elif current_label and label[2:] != current_label:
                chunks.append(
                    Chunk(
                        start_index=start_index,
                        end_index=index - 1,
                        label=current_label,
                    )
                )
                start_index, current_label = None, None

        if current_label:
            chunks.append(
                Chunk(
                    start_index=start_index,
                    end_index=len(labels) - 1,
                    label=current_label,
                )
            )

        return chunks

    def to_labels(self):
        labels = ["O"] * self.labels_size
        for chunk in self.chunks:
            labels[chunk.start_index] = "B-" + chunk.label
            for index in range(chunk.start_index + 1, chunk.end_index + 1):
                labels[index] = "I-" + chunk.label

        return labels
