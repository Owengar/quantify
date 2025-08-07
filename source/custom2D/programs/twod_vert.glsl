#version 430


in vec2 vert;
in vec2 in_text;
out vec2 v_text;


//margin_percentages
uniform vec2 margin_percentages;

//

//camera viewport and its derived vars
uniform vec2 camera_viewport_start;
uniform vec2 camera_viewport;
vec2 camera_viewport_inverse = 1.0/camera_viewport;
//


const vec2 NONE_ONE = vec2(-1.0, 1.0);
const vec2 ONE_NONE = vec2(1.0, -1.0);
const vec2 ONE_ONE = vec2(1.0, 1.0);

void main()
{


    gl_Position = vec4(vert*ONE_NONE*(ONE_ONE-margin_percentages)*camera_viewport+margin_percentages+(camera_viewport_inverse*camera_viewport_start*NONE_ONE), -0.5, 1.0);
    //gl_Position = vec4(vert, -0.5, 1.0);
    v_text = in_text;

}