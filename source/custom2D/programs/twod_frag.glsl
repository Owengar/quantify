#version 430
precision mediump float;



uniform sampler2D draw_texture;

in vec2 v_text; 
out vec4 f_color;








void main()
{

    vec4 draw_texture = texture(draw_texture, v_text);
    if (draw_texture.rgb == vec3(0.0, 0.0, 0.0))
    {
        f_color = vec4(0.0, 0.0, 1.0, 1.0);
    }
    else
    {
    f_color = draw_texture.bgra;
    }
}