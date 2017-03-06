CC = gcc
#For older gcc, use -O3 or -O2 instead of -Ofast
CFLAGS = -lm -pthread -Ofast -march=native -funroll-loops -Wno-unused-result
G_BUILDDIR := glove/build
G_SRCDIR := glove/src

g : g_dir g_glove g_shuffle g_cooccur g_vocab_count

g_dir :
	mkdir -p $(G_BUILDDIR)
g_glove : $(G_SRCDIR)/glove.c
	$(CC) $(G_SRCDIR)/glove.c -o $(G_BUILDDIR)/glove $(CFLAGS)
g_shuffle : $(G_SRCDIR)/shuffle.c
	$(CC) $(G_SRCDIR)/shuffle.c -o $(G_BUILDDIR)/shuffle $(CFLAGS)
g_cooccur : $(G_SRCDIR)/cooccur.c
	$(CC) $(G_SRCDIR)/cooccur.c -o $(G_BUILDDIR)/cooccur $(CFLAGS)
g_vocab_count : $(G_SRCDIR)/vocab_count.c
	$(CC) $(G_SRCDIR)/vocab_count.c -o $(G_BUILDDIR)/vocab_count $(CFLAGS)

g_clean:
	rm -rf g_glove g_shuffle g_cooccur g_vocab_count # g_build
