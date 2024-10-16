import re
from haystack.schema import Document
from haystack.document_stores import InMemoryDocumentStore
from haystack.telemetry import tutorial_running
from haystack.nodes import PreProcessor
from haystack.nodes import EmbeddingRetriever, BM25Retriever
from haystack.nodes import JoinDocuments, SentenceTransformersRanker
from haystack.pipelines import Pipeline

SP_Str_List = [["本案现已审理终结。"], 
              ["原告*向本院提出诉讼请求", "原告*诉称", ""],
              ["被告*辩称", "被告*答辩",],
              ["上述事实"],
              ["本院经审理认定事实如下", "经审理查明"],
              ["本院认为"],
              ["判决如下", ],
              ["如不服本判决",],
              ["附：本案适用的相关法律条文"]]
    
preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=True,
    split_by="word",
    split_length=512,
    split_overlap=32,
    split_respect_sentence_boundary=True,
)

class SpecialSubStringTextSplitter:
    """
    Text Splitter:
        To initialize, use the list of substrings that represent 'splitters' of the semi-structured texts.
        To split texts, use the method self.split(text, direction).
        'direction' can be 'forward' (group with preceding text) or 'backward' (group with following text).
    """
    def __init__(self, sp_substrings, split_direction='backward'):
        self.keywords = [item for sublist in sp_substrings for item in sublist if item]
        self.patterns = [self._prepare_pattern(keyword) for keyword in self.keywords]
        self.split_direction = split_direction

    def _prepare_pattern(self, keyword):
        escaped_keyword = re.escape(keyword).replace('\\*', '.*?')
        return f'({escaped_keyword})'

    def split(self, text, direction=None):
        """
        Split text by self.sp_substrings and return the list of split text segments.
        If direction is 'forward', include the keyword with the preceding text.
        If direction is 'backward', include the keyword with the following text.
        """
        if direction == None:
            direction = self.split_direction
        pattern = '|'.join(self.patterns)
        parts = []
        last_end = 0
        for match in re.finditer(pattern, text):
            if direction == 'forward':
                if match.start() != last_end:
                    parts.append(text[last_end:match.start()].strip())
                parts.append(text[match.start():match.end()])
                last_end = match.end()
            elif direction == 'backward':
                parts.append(text[last_end:match.start()].strip())
                last_end = match.start()  # Keyword starts the next part
        if last_end < len(text):
            parts.append(text[last_end:].strip())

        if direction == 'backward':
            combined_parts = []
            for i in range(len(parts) - 1):
                if re.match(pattern, parts[i]):
                    combined_parts.append(parts[i] + parts[i+1])
                elif not re.match(pattern, parts[i+1]):
                    combined_parts.append(parts[i])
            combined_parts.append(parts[-1])  # Add the last part
            return combined_parts
        return parts
    
def SplittedList2Doc(splitted_doc):
    docs = []
    for i, text in enumerate(splitted_doc):
        docs.append(Document(content=text, meta={"id": str(i)}))
    return docs

def ParaDict2Doc(paradict_doc, verbose = False):
    docs = []
    id = 0
    for key, value in paradict_doc.items():
        if isinstance(value, str):
            docs.append(Document(content=value, meta={"position": key, "id": id}))
            id += 1
        elif isinstance(value, list):
            for str_value in value:
                docs.append(Document(content=str_value, meta={"position": key, "id": id}))
                id += 1
        else:
            if verbose:
                print(f"Warning: {value} is neither str or list")
    return docs

def ParaDict2Doc_v1(paradict_doc, verbose = False):
    docs = []
    id = 0
    for key, value in paradict_doc.items():
        if isinstance(value, str):
            docs.append(Document(content=value, meta={"position": key, "id": id}))
            id += 1
        elif isinstance(value, list):
            for str_value in value:
                docs.append(Document(content=str_value, meta={"position": key, "id": id}))
                id += 1
        elif isinstance(value, dict):
            for key_value, str_value in value.items():
                if isinstance(str_value, str):
                    docs.append(Document(content=str_value, meta={"position": key, "sub_position": key_value, "id": id}))
                    id += 1
                elif isinstance(str_value, list):
                    for str_value_ in str_value:
                        docs.append(Document(content=str_value_, meta={"position": key, "sub_position": key_value, "id": id}))
                        id += 1
                else:
                    if verbose:
                        print(f"Warning: {str_value} is not str")
        else:
            if verbose:
                print(f"Warning: {value} is neither str, list, or dict")
    return docs

class DocData:
    """
    DocData is used for Retriever as database
    Input: Document Data, Text Segmenter
    Store: original doc string, segmented doc data
    """
    def __init__(self, doc_str, text_splitter):
        self.doc_str = doc_str
        self.text_splitter = text_splitter
        self.docs = []
        
    def form_document(self):
        splitted_texts = self.text_splitter.split(self.doc_str, 'backward')
        self.docs = SplittedList2Doc(splitted_texts)


preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=True,
    split_by="word",
    split_length=512,
    split_overlap=32,
    split_respect_sentence_boundary=True,
)



class DocStore:
    """
    DocStore stores Retrievers and textual Database
    
    """
    def __init__(self, preprocessor=None, doc_data=None):
        self.doc_data = doc_data
        if preprocessor!=None:
            self.preprocessor = preprocessor
            #self.docs = self.doc_data.docs
            self.docs_to_index = self.preprocessor.process(doc_data)
        else:
            self.preprocessor = preprocessor
            self.docs_to_index = doc_data
        self.document_store = None
        self.sparse_retriever = None
        self.dense_retriever = None
        self.pipeline = None
    
    def init_retriever(self, embedding_dim=384, embedding_model="sentence-transformers/all-MiniLM-L6-v2", ranker_model_name="cross-encoder/ms-marco-MiniLM-L-6-v2", use_gpu=True, scale_score=False):
        self.document_store = InMemoryDocumentStore(use_bm25=True, embedding_dim=embedding_dim)
        self.sparse_retriever = BM25Retriever(document_store=self.document_store)
        self.dense_retriever = EmbeddingRetriever(
            document_store=self.document_store,
            embedding_model=embedding_model,
            use_gpu=use_gpu,
            scale_score=scale_score,
        )
        self.document_store.delete_documents()
        self.document_store.write_documents(self.docs_to_index)
        self.document_store.update_embeddings(retriever=self.dense_retriever)
        self.join_documents = JoinDocuments(join_mode="concatenate")
        self.rerank = SentenceTransformersRanker(model_name_or_path=ranker_model_name)

    def create_pipeline(self):
        self.pipeline = Pipeline()
        self.pipeline.add_node(component=self.sparse_retriever, name="SparseRetriever", inputs=["Query"])
        self.pipeline.add_node(component=self.dense_retriever, name="DenseRetriever", inputs=["Query"])
        self.pipeline.add_node(component=self.join_documents, name="JoinDocuments", inputs=["SparseRetriever", "DenseRetriever"])
        self.pipeline.add_node(component=self.rerank, name="ReRanker", inputs=["JoinDocuments"])
    
    def retrieve(self, query, sparse_top_k = 10, dense_top_k = 10, join_top_k = 15, reranker_topk = 5):
        prediction = self.pipeline.run(
            query=query,
            params={
                "SparseRetriever": {"top_k": sparse_top_k},
                "DenseRetriever": {"top_k": dense_top_k},
                "JoinDocuments": {"top_k_join": join_top_k},  # comment for debug
                # "JoinDocuments": {"top_k_join": 15, "debug":True}, #uncomment for debug
                "ReRanker": {"top_k": reranker_topk},
            },
        )
        return prediction["documents"]