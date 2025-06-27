import inspect
from django_web_components import component
from dataclasses import asdict, dataclass


@component.register("accordion")
class Accordion(component.Component):
    template_name = "pages/components/accordion.html"
    slots = ("inner_block", "header")

    def get_context(self, *args, **kwargs):
        return {
            "attributes": kwargs, 
            "slots": self.slots_dict
        }

@dataclass
class CarouselConfig:
    # Swiper parameters: https://swiperjs.com/swiper-api#parameters
    slides_per_view: int = 1
    effect: str = "fade"
    direction: str = "horizontal"
    loop: bool = True
    hide_bullets: bool = False
    enable_nav_buttons: bool = False
    enable_scrollbar: bool = False
    swiper_theme: str = "white-swiper"
    bullets_color: str = "false"
    # add more parameters here

    @classmethod
    def from_dict(cls, env):
        return cls(**{k: v for k, v in env.items() if k in inspect.signature(cls).parameters})

    def dict(self):
        return asdict(self)


@component.register("carousel")
class Carousel(component.Component):
    template_name = "pages/components/carousel/carousel.html"

    def get_context_data(self, **kwargs) -> dict:
        # todo: remove config entries from attributes dict
        config = CarouselConfig.from_dict(self.attributes)
        return {"config": config.dict()}


@component.register("carousel_slide")
class CarouselSlide(component.Component):
    template_name = "pages/components/carousel/carousel_slide.html"
