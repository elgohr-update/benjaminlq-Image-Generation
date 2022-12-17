"""Streamlit App
"""
import streamlit as st
import torch

import config
from dataloaders import dataloaders
from deploy.inference import InferVAE
from models import models

st.set_page_config("VAE_GAN")


@st.cache(allow_output_mutation=True)
def initialize_inferer():
    return InferVAE()


inferer = initialize_inferer()

data_imgs = {
    "mnist": str(config.DEPLOY_PATH / "images" / "mnist.png"),
    "fmnist": str(config.DEPLOY_PATH / "images" / "fmnist.png"),
    "cifar10": str(config.DEPLOY_PATH / "images" / "cifar10.png"),
}

st.title("VAE and GAN on MNIST, Fashion MNIST and CIFAR-10")

col1_recon_settings, col2_recon_settings, col3_recon_settings = st.columns(3)

with st.sidebar:
    dataset = st.selectbox("Dataset", ["mnist", "fmnist", "cifar10"])
    _, input_size = dataloaders[dataset]
    with st.expander("See sample images"):
        st.image(data_imgs[dataset])
    hidden_size = st.radio("Hidden Size", [2, 32, 64, 128])
    model_type = st.radio("Model", models.keys())

tab1, tab2, tab3 = st.tabs(
    ["Image Generation", "Image Reconstruction", "Image Interpolation"]
)

### Generation
with tab1:
    st.header("Image Generation")
    st.markdown(
        "Generate a random sample from Standard Gaussian Distribution from the Latent Space"
    )
    with st.form("Image Gen Form"):
        gen_random = st.form_submit_button("Generate Image")
        if gen_random:
            z = torch.randn(hidden_size)
            st.write(z)
            recon_img = inferer.decode(z, model_type, hidden_size, dataset)
            st.image(
                recon_img.permute(1, 2, 0).detach().numpy(),
                width=400,
                caption="Reconstructed Image",
            )

### Reconstruction
with tab2:
    st.header("Image Reconstruction")
    recon_class_no = st.selectbox("Class", config.CLASSES[dataset].keys())
    target_col, recon_col = st.columns(2)

    with st.form("Image Recon Form"):
        sample_img_recon = st.form_submit_button("Reconstruct Image")
        if sample_img_recon:
            with target_col:
                target_img = inferer.sample_image(
                    config.CLASSES[dataset][recon_class_no], dataset
                )
                st.image(
                    target_img.permute(1, 2, 0).detach().numpy(),
                    width=300,
                    caption="Original Image",
                )

            with recon_col:
                recon_img = inferer.reconstruction(
                    target_img, model_type, hidden_size, dataset
                )
                st.image(
                    recon_img.permute(1, 2, 0).detach().numpy(),
                    width=300,
                    caption="Reconstructed Image",
                )

with tab3:
    st.header("Image Interpolation")
    img1, img2 = st.columns(2)

    with img1:
        digit_class1 = st.selectbox("First Class", config.CLASSES[dataset].keys())
        first_img = inferer.sample_image(config.CLASSES[dataset][digit_class1], dataset)
        st.image(first_img.permute(1, 2, 0).detach().numpy(), width=300)

    with img2:
        digit_class2 = st.selectbox("Second Class", config.CLASSES[dataset].keys())
        second_img = inferer.sample_image(
            config.CLASSES[dataset][digit_class2], dataset
        )
        st.image(second_img.permute(1, 2, 0).detach().numpy(), width=300)

    with st.form("Image Interpolate Form"):
        interpolate_submit = st.form_submit_button("Interpolate Image")
        if interpolate_submit:
            intermediate_images = inferer.interpolate(
                first_img, second_img, model_type, hidden_size, dataset
            )
            st.image(intermediate_images.permute(1, 2, 0).detach().numpy(), width=650)

# streamlit run ./src/streamlit_app.py
