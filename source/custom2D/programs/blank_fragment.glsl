#version 430
precision mediump float;



uniform sampler2D label_texture;

in vec2 v_text; 
out vec4 f_color;








void main()
{

    vec4 label_texture = texture(label_texture, v_text);
    f_color = label_texture.bgra;
}