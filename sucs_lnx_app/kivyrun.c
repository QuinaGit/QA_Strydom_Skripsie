// gcc -Wall -L/usr/X11R6/lib -lX11 kivyrun.c -o kivyrun
#include <X11/Xlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

unsigned long RGB(Display *disp,
        unsigned char r,
        unsigned char g,
        unsigned char b)
{
    XColor xc;
    Colormap cm = DefaultColormap(disp, DefaultScreen(disp));

    xc.red = 257 * r;
    xc.green = 257 * g;
    xc.blue = 257 * b;

    XAllocColor(disp, cm, &xc);
    return xc.pixel;
}

int main(int argc, char *argv[])
{
        char cmdStr[1024];
        Display *disp;
        XWindowAttributes attr;
        XSetWindowAttributes myAttr;
        Window myWin, rootWin;
        int screen;
        GC gc;

        if (argc != 2) {
                fprintf(stderr, "Usage: %s SCRIPT_FILE_NAME\n", argv[0]);
                exit(1);
        }

        disp = XOpenDisplay(":0.0");
        if (disp == NULL) {
                fprintf(stderr, "Cannot open display\n");
                exit(1);
        }

        rootWin = DefaultRootWindow(disp);
        screen = DefaultScreen(disp);

        XGetWindowAttributes(disp, rootWin, &attr);

        myAttr.override_redirect = True;

        myWin = XCreateWindow(disp, RootWindow(disp, screen),
                0, 0, attr.width, attr.height, 0,
                CopyFromParent, CopyFromParent, CopyFromParent,
                CWOverrideRedirect, &myAttr);
        XMapWindow(disp, myWin);

        gc = XCreateGC(disp, myWin, 0, 0);
        XSetForeground(disp, gc, RGB(disp, 0, 0, 0));

        XFillRectangle(disp, myWin, gc, 0, 0, attr.width, attr.height);
        XFlush(disp);

        snprintf(cmdStr, 1024, "python %s", argv[1]);

        printf("%s\n", cmdStr);
        system(cmdStr);

        XCloseDisplay(disp);
        return 0;
}
