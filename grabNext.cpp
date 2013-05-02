#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#define SAMPLE 1
#define _FILE_OFFSET_BITS 64


// 10 MB buffer
unsigned char buff[10485760];

void extractFile (const char *path, unsigned long long start, unsigned long long end) {
    static char picBuff[9000000];
    static int fileIndex = 0;
    char outputPath[256];
    char metaPath[256];
    sprintf(outputPath, "%s-%06d.JPG", path, fileIndex);
    
    if ( 0 != fileIndex % SAMPLE ) {
        // fprintf(stdout, "Skipping creation of: %s (%d bytes) for sampling purposes\n", outputPath, end - start + 1);
        return;
    }

    if ( end - start + 1 > sizeof(picBuff) ) {
        fprintf(stderr, "WARNING: Picture too large for buffer, skipping: %d bytes\n", end - start + 1);
        return;
    }
    FILE *input = fopen(path, "r");
    FILE *output = fopen(outputPath, "w"); 
    if ( !output) {
        fprintf(stderr, "WARNING: Could not open output file %s\n", outputPath);
        return;
    }
    fseeko(input, start, SEEK_SET);
    int numRead = fread( picBuff, 1, end - start + 1, input );
    int numWrote = fwrite( picBuff, 1, end - start + 1, output );
    fprintf(stdout, "Wrote: %s from %llu to %llu (%d bytes)\n", outputPath, start, end, end - start + 1);
    fclose(input);
    fclose(output);

/*
    sprintf(metaPath, "%s-%06d.meta", path, fileIndex);
    FILE *meta = fopen(metaPath, "w");
    fprintf(meta, "From file \"%s\"\nImage started at byte %llu\nImage ended at byte %llu\nImage is %d bytes", path, start, end, end - start + 1);
    fclose(meta);
*/
 
    fileIndex++;

}
    

int main(int argc, const char *argv[]) {

    enum ReadState {
       OUTSIDE= 0,
       BETWEEN
    };

    fprintf(stdout, "Opening file %s\n", argv[1]);
    int input = open(argv[1], O_RDONLY);
    int fpos = 0;
    int bytesRead = 0;
    unsigned long long totalRead = 0;
    int numRead = 0;
    bool foundEof = false;
    unsigned long long startPos = 0;
    unsigned long long endPos = 0;
   
    ReadState state = OUTSIDE;

    while ( !foundEof ) {
    
        numRead = 0;

        // fill our buffer
        while ( numRead < sizeof(buff) ) {
            bytesRead = read( input, buff + numRead,  sizeof(buff) - numRead );
            if ( bytesRead < 0 ) {
                perror("Reading file");
            }
            if ( bytesRead == 0 ) {
                fprintf(stdout, "EOF occurred\n");
                foundEof = true;
                break;
            }
        
            numRead += bytesRead;
        }
         
        // look for stuff
        int indx = 1;
        for(; indx < numRead; indx++ ) {
            if ( state == BETWEEN
              && totalRead + indx - startPos > 5000000 ) {
               fprintf(stderr, "WARNING: went 5MB without finding end\n");
               state = OUTSIDE;
            }
            if ( 0xff == buff[indx-1]
              && 0xd9 == buff[indx]
              && state == BETWEEN ) {
                endPos = totalRead + indx;
                if ( endPos - startPos < 65536 ) {
                    // fprintf(stderr, "WARNING: too small -- skipping chunk of %llu bytes\n", endPos - startPos);
                    continue;
                }
                // fprintf(stdout, "JPG found from %llu to %llu (%d bytes)\n", startPos, endPos, endPos - startPos + 1);
                extractFile( argv[1], startPos, endPos );
                state = OUTSIDE;
            } 
            if ( indx >= 9 ) {
                if ( 0xff == buff[indx-9]
                  && 0xd8 == buff[indx-8] 
                  && 'E' == buff[indx-3]
                  && 'x' == buff[indx-2]
                  && 'i' == buff[indx-1]
                  && 'f' == buff[indx]
                  && state == OUTSIDE ) {
                    startPos = totalRead + indx - 9;
                    state = BETWEEN;
                    // fprintf(stdout, "Start jpg at %llu\n", startPos);
                }
            }
        }

        totalRead += numRead;
    }
    fprintf(stdout, "closing file\n");
    close(input);
}
