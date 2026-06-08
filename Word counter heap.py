"""
Programlama Lab 2 - Proje 3
TXT Dosyasındaki Kelime Sayısını Heap Yapısı ile Sıralayan Program

Heap anahtarları:
  1. Kelimenin ilk harfi (A'dan Z'ye - min heap gibi davranır)
  2. Aynı harfle başlayan kelimeler için frekans (en fazladan en aza - max heap)
"""

import sys
import re


# ─────────────────────────────────────────────
# Heap Düğümü
# ─────────────────────────────────────────────
class HeapNode:
    def __init__(self, word: str, count: int = 1):
        self.word = word                        # Kelime (orijinal büyük/küçük harf korunur)
        self.key1 = word[0].upper()             # 1. anahtar: ilk harf (büyük)
        self.count = count                      # 2. anahtar: frekans

    def __repr__(self):
        return f"HeapNode({self.word!r}, key1={self.key1!r}, count={self.count})"


# ─────────────────────────────────────────────
# İki Anahtarlı Heap
#
# Sıralama mantığı (min-heap karşılaştırması):
#   - Önce key1 (ilk harf) A → Z  (küçük harf < büyük harf demek)
#   - Eşit harfler için: count BÜYÜK olan daha "küçük" kabul edilir
#     (yani en yüksek frekans köke çıkar)
# ─────────────────────────────────────────────
class DualKeyHeap:
    def __init__(self):
        self._data: list[HeapNode] = []         # Heap dizisi
        self._index: dict[str, int] = {}        # word (büyük) → dizi indeksi

    # ── Yardımcı: karşılaştırma ──────────────
    def _less(self, i: int, j: int) -> bool:
        """i. düğüm j. düğümden heap sırasında 'önce' mi?"""
        a, b = self._data[i], self._data[j]
        if a.key1 != b.key1:
            return a.key1 < b.key1              # 1. anahtar: harf A→Z
        return a.count > b.count                # 2. anahtar: frekans büyük → önce

    # ── Yardımcı: swap ───────────────────────
    def _swap(self, i: int, j: int):
        di, dj = self._data[i], self._data[j]
        self._index[di.word.upper()] = j
        self._index[dj.word.upper()] = i
        self._data[i], self._data[j] = dj, di

    # ── Yukarı kabarcık ──────────────────────
    def _sift_up(self, i: int):
        while i > 0:
            parent = (i - 1) // 2
            if self._less(i, parent):
                self._swap(i, parent)
                i = parent
            else:
                break

    # ── Aşağı kabarcık ───────────────────────
    def _sift_down(self, i: int):
        n = len(self._data)
        while True:
            left  = 2 * i + 1
            right = 2 * i + 2
            best  = i
            if left  < n and self._less(left,  best): best = left
            if right < n and self._less(right, best): best = right
            if best == i:
                break
            self._swap(i, best)
            i = best

    # ── Ana işlem: kelime ekle / güncelle ────
    def add_word(self, word: str):
        """
        Kelimeyi heap'e ekle.
        Zaten varsa sadece count'unu artır ve heap'i yeniden düzenle.
        """
        key = word.upper()

        if key in self._index:
            # Kelime heap'te var → count artır, pozisyonu güncelle
            idx = self._index[key]
            self._data[idx].count += 1
            # Frekans arttı; bu düğüm "daha önce" gelmeli → sift_up yeterli
            self._sift_up(idx)
            # (sift_down gerekmez çünkü count sadece arttı)
        else:
            # Yeni kelime → sona ekle, yukarı kabarcıkla
            node = HeapNode(word)
            self._data.append(node)
            pos = len(self._data) - 1
            self._index[key] = pos
            self._sift_up(pos)

    # ── Kök elemanı al (sil) ─────────────────
    def pop(self) -> HeapNode:
        """En öncelikli düğümü heap'ten çıkar ve döndür."""
        if not self._data:
            raise IndexError("Heap boş")
        n = len(self._data)
        self._swap(0, n - 1)
        node = self._data.pop()
        del self._index[node.word.upper()]
        if self._data:
            self._sift_down(0)
        return node

    def __len__(self):
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0


# ─────────────────────────────────────────────
# Dosyayı Oku ve Heap'i Doldur
# ─────────────────────────────────────────────
def read_file_into_heap(filepath: str) -> DualKeyHeap:
    heap = DualKeyHeap()

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Noktalama işaretlerini temizle, kelimelere ayır
    words = re.findall(r"[A-Za-zÇçĞğİıÖöŞşÜü]+", text)

    for raw_word in words:
        # Büyük/küçük harf normalizasyonu: karşılaştırma için büyük harfe çevir,
        # ama görüntü için ilk harfi büyük yap
        word = raw_word.capitalize()
        heap.add_word(word)

    return heap


# ─────────────────────────────────────────────
# Çıktıyı Yazdır
# ─────────────────────────────────────────────
def print_results(heap: DualKeyHeap):
    print(f"\n{'Kelime':<25} {'Adet':>6}")
    print("-" * 33)

    while not heap.is_empty():
        node = heap.pop()
        print(f"{node.word:<25} {node.count:>6}")


# ─────────────────────────────────────────────
# Ana Program
# ─────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        filepath = input("TXT dosyasının yolunu girin: ").strip()
    else:
        filepath = sys.argv[1]

    try:
        heap = read_file_into_heap(filepath)
    except FileNotFoundError:
        print(f"Hata: '{filepath}' dosyası bulunamadı.")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: {e}")
        sys.exit(1)

    print(f"\n'{filepath}' dosyasındaki kelime sayıları (A→Z, aynı harfte çoktan aza):")
    print_results(heap)


if __name__ == "__main__":
    main()