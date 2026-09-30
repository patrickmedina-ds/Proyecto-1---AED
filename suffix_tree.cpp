// Suffix Tree (árbol de sufijos comprimido) - implementación propia en C++17
// Construcción por inserción de sufijos: O(n^2). Búsqueda de patrón: O(m + occ).
// Emite una traza JSON de cada paso para que la animación sea dirigida por la estructura real.
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <sstream>
using namespace std;

struct Node {
    int id;
    int parent;
    int start, end;            // etiqueta de la arista entrante = text[start, end)
    int suffixIndex;           // -1 si es nodo interno
    map<char, int> children;   // primer caracter de la arista -> hijo
};

class SuffixTree {
    string text;
    vector<Node> nodes;
    vector<string> stepsJson;

    int newNode(int parent, int s, int e, int suf) {
        nodes.push_back({(int)nodes.size(), parent, s, e, suf, {}});
        return (int)nodes.size() - 1;
    }
    static string esc(const string& s) {
        string r;
        for (char c : s) { if (c == '"' || c == '\\') r += '\\'; r += c; }
        return r;
    }
    string label(int id) const { return text.substr(nodes[id].start, nodes[id].end - nodes[id].start); }

    string treeJson() const {
        ostringstream o; o << "[";
        for (size_t i = 0; i < nodes.size(); i++) {
            const Node& n = nodes[i];
            o << (i ? "," : "") << "{\"id\":" << n.id << ",\"parent\":" << n.parent
              << ",\"label\":\"" << esc(label(n.id)) << "\",\"suffix\":" << n.suffixIndex
              << ",\"children\":[";
            bool first = true;
            for (auto& [c, ch] : n.children) { o << (first ? "" : ",") << ch; first = false; }
            o << "]}";
        }
        o << "]";
        return o.str();
    }
    void log(int suffix, const string& event, const vector<int>& path, int highlight) {
        ostringstream o;
        o << "{\"suffix\":" << suffix << ",\"suffixText\":\"" << esc(suffix >= 0 ? text.substr(suffix) : string())
          << "\",\"event\":\"" << event << "\",\"highlight\":" << highlight << ",\"path\":[";
        for (size_t i = 0; i < path.size(); i++) o << (i ? "," : "") << path[i];
        o << "],\"tree\":" << treeJson() << "}";
        stepsJson.push_back(o.str());
    }

    // Inserta el sufijo text[i..] en el árbol comprimido
    void insertSuffix(int i) {
        int cur = 0, pos = i;
        vector<int> path = {0};
        int n = (int)text.size();
        while (true) {
            char c = text[pos];
            auto it = nodes[cur].children.find(c);
            if (it == nodes[cur].children.end()) {           // Caso 1: no hay arista -> hoja nueva
                int leaf = newNode(cur, pos, n, i);
                nodes[cur].children[c] = leaf;
                path.push_back(leaf);
                log(i, "leaf", path, leaf);
                return;
            }
            int child = it->second;
            int len = nodes[child].end - nodes[child].start, k = 0;
            while (k < len && text[nodes[child].start + k] == text[pos + k]) k++;
            if (k == len) {                                   // arista consumida: bajar
                cur = child; pos += len; path.push_back(child);
                continue;
            }
            // Caso 2: el mismatch cae en medio de la arista -> partir arista
            int mid = newNode(cur, nodes[child].start, nodes[child].start + k, -1);
            nodes[cur].children[c] = mid;
            nodes[child].start += k;
            nodes[child].parent = mid;
            nodes[mid].children[text[nodes[child].start]] = child;
            int leaf = newNode(mid, pos + k, n, i);
            nodes[mid].children[text[pos + k]] = leaf;
            path.push_back(mid); path.push_back(leaf);
            log(i, "split", path, mid);
            return;
        }
    }

    void collectLeaves(int id, vector<int>& out) const {
        if (nodes[id].suffixIndex >= 0) out.push_back(nodes[id].suffixIndex);
        for (auto& [c, ch] : nodes[id].children) collectLeaves(ch, out);
    }

public:
    explicit SuffixTree(const string& s) : text(s + "$") {
        newNode(-1, 0, 0, -1);        // raíz
        log(-1, "root", {0}, 0);
        for (int i = 0; i < (int)text.size(); i++) insertSuffix(i);
    }

    // Busca un patrón; devuelve JSON con el camino recorrido y las ocurrencias
    string search(const string& p) const {
        int cur = 0, pos = 0;
        vector<int> path = {0};
        bool found = true;
        int endNode = 0;
        while (pos < (int)p.size()) {
            auto it = nodes[cur].children.find(p[pos]);
            if (it == nodes[cur].children.end()) { found = false; break; }
            int child = it->second;
            int len = nodes[child].end - nodes[child].start, k = 0;
            while (k < len && pos < (int)p.size() && text[nodes[child].start + k] == p[pos]) { k++; pos++; }
            path.push_back(child);
            if (pos == (int)p.size()) { endNode = child; break; }
            if (k < len) { found = false; break; }
            cur = child;
        }
        vector<int> occ;
        if (found) collectLeaves(endNode, occ);
        ostringstream o;
        o << "{\"pattern\":\"" << esc(p) << "\",\"found\":" << (found ? "true" : "false") << ",\"path\":[";
        for (size_t i = 0; i < path.size(); i++) o << (i ? "," : "") << path[i];
        o << "],\"occurrences\":[";
        for (size_t i = 0; i < occ.size(); i++) o << (i ? "," : "") << occ[i];
        o << "]}";
        return o.str();
    }

    string traceJson(const vector<string>& patterns) const {
        ostringstream o;
        o << "{\"text\":\"" << esc(text) << "\",\"steps\":[";
        for (size_t i = 0; i < stepsJson.size(); i++) o << (i ? "," : "") << stepsJson[i];
        o << "],\"searches\":[";
        for (size_t i = 0; i < patterns.size(); i++) o << (i ? "," : "") << search(patterns[i]);
        o << "]}";
        return o.str();
    }
};

// Uso: ./suffix_tree <texto> [patron1 patron2 ...]   (texto "" = caso vacío)
int main(int argc, char** argv) {
    string s = argc > 1 ? argv[1] : "banana";
    vector<string> pats;
    for (int i = 2; i < argc; i++) pats.push_back(argv[i]);
    SuffixTree st(s);
    cout << st.traceJson(pats) << "\n";
}
