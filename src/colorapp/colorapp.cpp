//cppimport
#include "pybind11/pybind11.h"
#include <list>
#include <tuple>

namespace py = pybind11;

//threaded function that takes and returns std::list<std::tuple<int>>
std::list<std::tuple<int>> recolor_thread(std::list<std::tuple<int>> img, int height; int width, std::tuple<int> rgb, float intensity){
    //recolor and manage return
    for(type_t i=0; i<=height*width; i++){
        for(type_t j=0; j<3; j++){
            img[i][j]=round(img[i][j] * (1-intensity) + rgb[j] * intensity);
        }
    }

    return(img);
}

PYBIND11_MODULE(recolor, m){
    m.doc() = "Python interface calling cpp to recolor. See src/colorapp/readme.md for details.";
    m.def("recolor", &recolor_thread, "Function calling recoloring.");
}
/*
<%
setup_pybind11(cfg)
<%
 */