from litellm import completion
import os
import re

def associate_citations_with_text(text, citations):
    """
    Scans the text for bracketed references (e.g., [1], [2], etc.),
    and associates them with the corresponding entry in the `citations` list.
    
    :param text: The text containing bracketed references
    :param citations: A list of citation URLs (list indices correspond to [1], [2], etc.)
    :return: A list of dictionaries, each containing:
             {
                 'original_line': The original line of text (with references),
                 'clean_line': The line with reference markers removed,
                 'citations': A list of citation URLs corresponding to the references
             }
    """

    # Split the text into lines
    lines = text.strip().split('\n')
    
    # This list will hold the result for each line
    line_citations = []
    
    for line in lines:
        # Find all bracketed references like [1], [2], [3], etc.
        refs = re.findall(r'\[(\d+)\]', line)
        
        # Remove the bracket references from the line to create a "clean" version
        clean_line = re.sub(r'\[\d+\]', '', line).strip()
        
        # Map each reference (e.g. "1") to its citation in the list
        associated_citations = []
        for ref in refs:
            index = int(ref) - 1  # bracketed refs are 1-based; Python lists are 0-based
            if 0 <= index < len(citations):
                associated_citations.append(citations[index])
            else:
                associated_citations.append(f"Unknown citation index: {ref}")
        
        line_citations.append({
            'original_line': line,
            'clean_line': clean_line,
            'citations': associated_citations
        })
    
    return line_citations


response = completion(
    model="perplexity/sonar-pro",
    messages = [
        {
            "role": "system",
            "content": (
                "You are an artificial intelligence assistant and you need to "
                "engage in a helpful, detailed, polite conversation with a user."
            ),
        },
        {
            "role": "user",
            "content": (
                "How many stars are in the universe?"
            ),
        },
    ]
)
text, citations = response.choices[0].message.content, response.citations

results = associate_citations_with_text(text, citations)

# Print out the results
for item in results:
    print("Original Line:")
    print(item['original_line'])
    print("Clean Line:")
    print(item['clean_line'])
    print("Associated Citations:")
    for c in item['citations']:
        print(f"  - {c}")
    print("-" * 60)