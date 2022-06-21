#include <iostream>
#include <SFML/Graphics.hpp>
#include <SFML/Network.hpp>
#include <math.h>
#include <tuple>
#define PI 3.1415926535897932384626433832795

using namespace std;

/*
V2 News :
- Cast_ray, render and AFE functions are now one function
- Deleted draw_map_top_view and line functions
*/

const int screen_size[2] = {1280,720};
const int texture_size[2] = {16,16};
const int sprite_size[2] = {32,32};
const int map_size[2] = {16,11};


int Map[11][16] ={{1,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1},
                  {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
                  {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
                  {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
                  {1,0,0,0,1,0,3,2,0,0,0,0,0,0,0,1},
                  {1,0,0,0,0,0,3,3,0,0,1,0,0,0,0,1},
                  {1,1,2,3,0,0,0,0,0,0,1,0,0,1,0,1},
                  {1,0,0,0,0,0,0,0,0,0,1,0,0,1,0,1},
                  {1,0,0,0,0,0,0,0,0,0,2,1,0,1,0,1},
                  {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
                  {1,1,1,1,1,3,3,1,1,1,1,1,1,2,1,1}};

int Floor_Map[11][16] ={{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}};

double player_x = 3.2;
double player_y = 2.5;
double player_a = 0.0;

double m_angle;

const int FOV = 60;
const int y_FOV = screen_size[1]*FOV/screen_size[0];
const float RTX = 1.0f;
const double detail = screen_size[0]/FOV * RTX;
const double y_detail = screen_size[1]/y_FOV * RTX;
const double ray_width = screen_size[0]/(FOV*detail);
const double player_height = 1.8; // !!! Relative to tile size

const sf::Keyboard::Key RIGHT = sf::Keyboard::D;
const sf::Keyboard::Key LEFT = sf::Keyboard::Q;
const sf::Keyboard::Key UP = sf::Keyboard::Z;
const sf::Keyboard::Key DOWN = sf::Keyboard::S;

const int max_sprite_count = 64;

sf::Clock monotonic;
double delta = 0;

sf::VertexArray quads_buffer(sf::Quads);
// Textures
sf::Image walls_textures[10];
sf::Image sprites_textures[10];

sf::Color Colors[] = {sf::Color(0,0,0),sf::Color(255,0,0),sf::Color(0,255,0),sf::Color(0,0,255)};

sf::RenderWindow app(sf::VideoMode(screen_size[0], screen_size[1]), "WAW");

int sprite_counter = 0;

class Sprite {
    public:
        double position_x;
        double position_y;
        double direction;
        int front_texture_index;
        int back_texture_index;
        bool no_rotation;
        int ID;
        int alive = false;

        void init(double pos_x, double pos_y, double dir, bool no_rot,int front_tex_index, int back_tex_index = -1) {
            ID = sprite_counter;
            sprite_counter++;
            position_x = pos_x;
            position_y = pos_y;
            direction = dir;
            no_rotation = no_rot;
            front_texture_index = front_tex_index;
            back_texture_index = back_tex_index;
            alive = true;
        }
};

Sprite sprites[max_sprite_count];

int add_sprite(Sprite sprite) {
    for(int s = 0; s < max_sprite_count; s++) {
        if(!sprites[s].alive) {
            sprites[s] = sprite;
            return s;
        }
    }
    return -1;
}

class Door { // Crap.
    private:
        bool moving = false;
        bool opened = false;
        double pos_x_modifier = 0;
        double pos_y_modifier = 0;

    public:
        int position_x,position_y,direction,texture_index,sprite_index;
        Sprite sprite;
        bool alive = false;
        void init(int pos_x, int pos_y, int dir, int tex_index) {
            position_x = pos_x;
            position_y = pos_y;
            direction = dir;
            texture_index = tex_index;
            if(dir%2) sprite.init(pos_x + 0.5, pos_y + 0.5, 0.0, false, texture_index, texture_index);
            else sprite.init(pos_x + 0.5, pos_y + 0.5, PI/2, false, texture_index, texture_index);
            sprite_index = add_sprite(sprite);
            alive = true;
        }

        void open() {
            if(opened) return;
            moving = true;
        }
        void close() {
            if(!opened) return;
            moving = true;
        }

        void update() {
            if(!moving) return;
            int way;
            if(opened) way = 1;
            else way = -1;
            if(direction%2) {
                pos_x_modifier += way * 0.5 * delta;
                if(abs(pos_x_modifier) >= 1) {moving = false; opened = !opened;}
            } else {
                pos_y_modifier += way * 0.5 * delta;
                if(abs(pos_y_modifier) >= 1) {moving = false; opened = !opened;}
            }
        }



};

void sort_sprites() {
    Sprite sorted_sprites[max_sprite_count];
    float dtp,other_dtp;
    int tier;
    for(int s = 0; s < max_sprite_count; s++) {
        if(!sprites[s].alive) continue;
        dtp = sqrt(pow(player_x-sprites[s].position_x,2) + pow(player_y-sprites[s].position_y, 2));
        tier = 0;
        for(int t = 0; t < max_sprite_count; t++) {
            if(t==s or !sprites[s].alive) continue;
            other_dtp = sqrt(pow(player_x-sprites[t].position_x,2) + pow(player_y-sprites[t].position_y, 2));
            if(dtp < other_dtp or dtp == other_dtp and sprites[s].ID > sprites[t].ID) {
                tier+=1;
            }
        }
        sorted_sprites[tier] = sprites[s];
    }
    for(int i = 0; i < max_sprite_count; i++) sprites[i] = sorted_sprites[i];
}

double radians(double degrees) {
    return degrees*PI/180.0;
}

double degrees(double radians) {
    return radians*180/PI;
}

void load_textures() {
    walls_textures[0].loadFromFile("resources/stone_wall.png");
    walls_textures[1].loadFromFile("resources/broken_stone_wall.png");
    walls_textures[2].loadFromFile("resources/mossy_stone_wall.png");

    sprites_textures[0].loadFromFile("resources/ennemy_front.png");
    sprites_textures[1].loadFromFile("resources/ennemy_back.png");
    sprites_textures[2].loadFromFile("resources/door.png");

}

sf::Color shade_color(sf::Color color, double shade) {
    return sf::Color(color.r*shade,color.g*shade,color.b*shade);
}

tuple<int,int,bool> AIE(int x,int y) {
    int new_x=max(min(x,map_size[0]-1),0);
    int new_y=max(min(y,map_size[1]-1),0);
    return {new_x,new_y,new_x!=x or new_y!=y};
}

void add_rect_to_buffer(double x, double y, double size_x, double size_y, sf::Color color) {
    quads_buffer.append(sf::Vertex(sf::Vector2f(  x,   y), color));
    quads_buffer.append(sf::Vertex(sf::Vector2f(  x + size_x, y), color));
    quads_buffer.append(sf::Vertex(sf::Vector2f(x + size_x, y + size_y), color));
    quads_buffer.append(sf::Vertex(sf::Vector2f(x, y + size_y), color));

}

void cast_ray_and_render(double x, double y, double angle, double angle_modifier, int ray_id) {
    double V_d = 1000000 ; double H_d = 1000000;
    // Horizontal
    double H_first_x,H_first_y,H_xStep,H_yStep,H_y_modifier,H_x,H_y,x_offset,y_offset;
    int H_map_value,V_map_value;

    if(abs(sin(angle))>10e-5) {
        if(sin(angle)>0) {
            H_first_y = ceil(y) - y;
            H_y_modifier = 0.1;
            H_yStep = 1;
        } else {
            H_first_y = int(y)-y;
            H_y_modifier = -0.1;
            H_yStep = -1;
        }
        H_first_x = H_first_y/tan(angle);
        H_xStep = 1/tan(H_yStep*angle);

        for(int H_i = 0; H_i<2048; H_i++) {
            H_x = x+H_first_x + H_xStep*H_i;
            H_y = y+H_first_y + H_yStep*H_i;
            auto [H_mx,H_my,changed]=AIE(int(H_x),int(H_y+H_y_modifier));

            H_map_value = Map[H_my][H_mx];
            if(H_map_value or changed) {
                H_d = sqrt(pow(H_first_x + H_xStep*H_i, 2) + pow(H_first_y + H_yStep*H_i, 2));
                break;
            }
        }
    }
    // Vertical
    double V_first_x,V_first_y,V_xStep,V_yStep,V_x_modifier,V_x,V_y;
    if(abs(cos(angle))>10e-5) {
        if(cos(angle)>0) {
            V_first_x = ceil(x) - x;
            V_x_modifier = 0.1;
            V_xStep = 1;
        } else {
            V_first_x = int(x) - x;
            V_x_modifier = -0.1;
            V_xStep = -1;
        }
        V_first_y = V_first_x*tan(angle);
        V_yStep = tan(V_xStep*angle);

        for(int V_i = 0; V_i<2048; V_i++) {
            V_x = x+V_x_modifier + V_xStep*V_i;
            V_y = y+V_first_y + V_yStep*V_i;
            auto [V_mx,V_my,changed] = AIE(int(V_x+V_first_x),int(V_y));

            V_map_value = Map[V_my][V_mx];
            if(V_map_value or changed) {
                V_d = sqrt(pow(V_first_x + V_xStep*V_i, 2) + pow(V_first_y + V_yStep*V_i, 2));
                break;
            }
        }
    }

    double distance = min(V_d,H_d);
    // Rendering walls
    double shade,offset;
    int map_value;
    if(distance == H_d) {
        if(sin(angle)>0) {
            x_offset = H_x - int(H_x);
        } else {
            x_offset = ceil(H_x) - H_x;
        }
        shade = 0.8;
        offset = x_offset;
        map_value = H_map_value;
    } else {
        if(cos(angle)<0) {
            y_offset = V_y - int(V_y);
        } else {
            y_offset = ceil(V_y) - V_y;
        }
        shade = 1.0;
        offset = y_offset;
        map_value = V_map_value;
    }
    float m_distance = cos(angle_modifier)*distance; // Avoid Fisheye Effect
    double ray_height = (300*screen_size[1]/222)/m_distance;

    for(int i = 0;i<texture_size[1];i++) {
        add_rect_to_buffer(ray_id*ray_width, screen_size[1]/2 - ray_height/2 + i*ray_height/texture_size[1],
                           ray_width, ray_height/texture_size[1],
                           shade_color(walls_textures[map_value-1].getPixel(int(offset*texture_size[0]),i),shade));
    }

    // Sprites
    double atpv,dtp,m_dtp,dtsc,sprite_height,pixel_height;
    int sprite_texture_index;
    sf::Color pixel;
    for(int s = 0; s < max_sprite_count; s++) {
        if(!sprites[s].alive) continue;
        atpv = -atan2(sprites[s].position_y - y, sprites[s].position_x - x) + angle;
        if(int(degrees(atpv + 2*PI))%360 > FOV/2 and int(degrees(atpv + 2*PI))%360< 360-FOV/2) continue;
        dtp = sqrt(pow(x-sprites[s].position_x,2) + pow(y-sprites[s].position_y, 2));
        if(dtp>distance + 0.01) continue;
        dtsc = tan(atpv)*dtp;
        //m_dtp = sqrt(pow(dtp, 2) + pow(dtsc, 2));
        if(!sprites[s].no_rotation) dtsc /= abs(cos(sprites[s].direction + atpv - angle));
        if(abs(dtsc) > 0.5) continue;

        if(cos(sprites[s].direction + atpv - angle)<0 or sprites[s].no_rotation) sprite_texture_index = sprites[s].front_texture_index;
        else sprite_texture_index = sprites[s].back_texture_index;

        // Render
        sprite_height = (300*screen_size[1]/222)/dtp;
        pixel_height = sprite_height/sprite_size[1];
        for(int t = 0; t < sprite_size[1]; t++) {
            pixel = sprites_textures[sprite_texture_index].getPixel(int(sprite_size[1]*(dtsc + 0.5)),t);
            add_rect_to_buffer(ray_id*ray_width, screen_size[1]/2 - pixel_height*(sprite_size[1]/2) + t*pixel_height, ray_width, pixel_height, pixel);

        }
    }

}

void game()
{
    // Font stuff
    sf::Font arial;
    arial.loadFromFile("resources/Arial.ttf");
    // FPS counter init
    double oldClock = 0;
    double currentClock;

    sf::Color color;
    int nb;
    double shade;
    // Load a sprite to display
    sprites[0].init(1.0,1.5,0.0,0,0,1);
    sprites[1].init(4.5,2.5,0.0,0,0,1);
    sprites[2].init(2.5,3.5,0.0,0,0,1);
    sprites[3].init(1.5,2.5,0.0,0,0,1);

    load_textures();
	// Start the game loop
	int counter = 0;
     while (app.isOpen())
    {
        // Process events
        sf::Event event;
        while (app.pollEvent(event))
        {
            // Close window : exit
            if (event.type == sf::Event::Closed)
                app.close();
        }
        // Get inputs
        if(sf::Keyboard::isKeyPressed(RIGHT)) player_a += PI/2 * delta;
        if(sf::Keyboard::isKeyPressed(LEFT)) player_a -= PI/2 * delta;
        if(sf::Keyboard::isKeyPressed(UP) & !Map[int(player_y+sin(player_a)/4)][int(player_x+cos(player_a)/4)]) {
            player_x += cos(player_a)*2*delta; player_y += sin(player_a)*2*delta;}
        if(sf::Keyboard::isKeyPressed(DOWN) & !Map[int(player_y-sin(player_a)/4)][int(player_x-cos(player_a)/4)]) {
            player_x -= cos(player_a)*2*delta; player_y -= sin(player_a)*2*delta;}
        if(player_a < 0) player_a += 2*PI;
        if(player_a > 2*PI) player_a -= 2*PI;


        // Clear screen
        app.clear();
        quads_buffer.clear();
        // Update the window

        // Rendering
        nb = 0;
        // Sky & floor
        add_rect_to_buffer(0, 0, screen_size[0], screen_size[1]/2, sf::Color(0,255,255));
        add_rect_to_buffer(0, screen_size[1]/2, screen_size[0], screen_size[1]/2, sf::Color(100,100,100));
        //Walls
        for(double modifier = -FOV*detail/2; modifier <= FOV*detail/2; modifier++) {
            cast_ray_and_render(player_x, player_y, player_a + radians(modifier/detail), radians(modifier/detail),nb);
            nb++;
        }

        app.draw(quads_buffer);
        app.display();


        // Fancy FPS action
        currentClock = monotonic.getElapsedTime().asSeconds();
        delta = currentClock - oldClock;
        oldClock = currentClock;
        counter++;
        if(counter%10 == 0) {
            app.setTitle("Super jeu : FPS:"+to_string(int(1/delta)));
            counter = 0;
            sort_sprites();
        }
    }
}

sf::TcpSocket S;
int main() {

    if(S.connect("192.168.159.42", 53000) != sf::Socket::Done) {cout << "Server unreachable" <<endl;}

    char data[4];
    std::size_t received;

    if (S.receive(data, 4, received) != sf::Socket::Done) {cout << "TCP error at line " << __LINE__ << endl;}

    cout << data[0] << endl;

    return 0;
}
