class ESIndex:
    index_delete = """{{
        "query": {{
            "term": {{
                "file_id": "{file_id}"
            }}
        }}
    }}"""

    index_search_content = """{{
      "size": 10,
      "timeout": "3s",
      "query": {{
        "bool": {{
          "should": [
            {{
              "multi_match": {{
                "query": "{query}",
                "fields": ["content^3", "summary^1.5"],
                "type": "best_fields",
                "analyzer": "ik_smart",
                "operator": "and",
                "minimum_should_match": "70%",
                "boost": 2.5
              }}
            }},
            {{
              "match_phrase": {{
                "content": {{
                  "query": "{query}",
                  "slop": 1,
                  "boost": 3.0
                }}
              }}
            }},
            {{
              "match_phrase": {{
                "summary": {{
                  "query": "{query}",
                  "slop": 1,
                  "boost": 1.8
                }}
              }}
            }}
          ],
          "minimum_should_match": 1
        }}
      }}
    }}"""

    index_search_summary = """{{
          "size": 10,
          "timeout": "3s",
          "query": {{
            "bool": {{
              "should": [
                {{
                  "match": {{
                    "summary": {{
                      "query": "{query}",
                      "analyzer": "ik_smart",
                      "operator": "and",
                      "minimum_should_match": "70%",
                      "boost": 2.2
                    }}
                  }}
                }},
                {{
                  "match_phrase": {{
                    "summary": {{
                      "query": "{query}",
                      "slop": 1,
                      "boost": 2.8
                    }}
                  }}
                }}
              ],
              "minimum_should_match": 1
            }}
          }}
        }}"""

    index_config = """{
      "settings": {
        "analysis": {
          "analyzer": {
            "ik_analyzer": {
              "type": "custom",
              "tokenizer": "ik_smart"
            }
          }
        }
      },
      "mappings": {
        "properties": {
          "chunk_id": {
            "type": "keyword"
          },
          "content": {
            "type": "text",
            "analyzer": "ik_analyzer"
          },
          "summary": {
            "type": "text",
            "analyzer": "ik_analyzer"
          },
          "file_id": {
            "type": "keyword"
          },
          "knowledge_id": {
            "type": "keyword"
          },
          "file_name": {
            "type": "keyword"
          },
          "update_time": {
            "type": "date",
            "format": "strict_date_optional_time||epoch_millis"
          }
        }
      }
    }"""
