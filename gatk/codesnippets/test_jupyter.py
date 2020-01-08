{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "Kfu2opPl_sYs"
   },
   "source": [
    "# GATK Germline Variant Discovery Tutorial <a class=\"tocSkip\">"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "XfB42nVh_sYt"
   },
   "source": [
    "**October 2019**  \n",
    "\n",
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image1.png\" alt=\"drawing\" width=\"40%\" align=\"left\" style=\"margin:0px 20px\"/> \n",
    "<font size=\"4\">The tutorial demonstrates an effective workflow for joint calling germline SNPs and indels in cohorts of multiple samples. The workflow applies to whole genome or exome data. Specifically, the tutorial uses a trio of WG sample snippets to demonstrate HaplotypeCaller's GVCF workflow for joint variant analysis. We use a GenomicsDB database structure, perform a genotype refinement based on family pedigree, and evaluate the effects of refinement.</font>\n",
    "\n",
    "_This tutorial was last tested with the GATK v4.1.3.0 and IGV v2.7.0._\n",
    " See [GATK Tool Documentation](https://software.broadinstitute.org/gatk/documentation/tooldocs/4.1.3.0/) for further information on the tools we use."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "CFlXtCPE_sYu"
   },
   "source": [
    "# Set up your Notebook\n",
    "## Set runtime values\n",
    "If you opened this notebook and didn't adjust any runtime values, now's the time to edit them. Click on the gear icon in the upper right to edit your Notebook Runtime. Set the values as specified below:\n",
    "\n",
    "| Runtime Environment | Value |\n",
    "| ------ | ------ |\n",
    "| CPU | 4 |\n",
    "| Disk size | 100 GB |\n",
    "| Memory | 15 GB |\n",
    "| Startup Script | `gs://gatk-tutorials/scripts/install_gatk_4130_with_igv2.sh` |\n",
    "\n",
    "Click the \"Update\" button when you are done, and Terra will begin to create a new runtime with your settings. When it is finished, it will pop up asking you to apply the new settings.\n",
    "\n",
    "## Check kernel type\n",
    "A kernel is a _computational engine_ that executes the code in the notebook. For this particular notebook, we will be using a Python 3 kernel so we can execute GATK commands using _Python Magic_ (`!`). In the upper right corner of the notebook, just under the Notebook Runtime, it should say `Python3`. If this notebook isn't running a Python 3 kernel, you can switch it by navigating to the Kernel menu and selecting `Change kernel`.\n",
    "\n",
    "## Set up your files\n",
    "Your notebook has a temporary folder that exists so long as your cluster is running. To see what files are in your notebook environment at any time, you can click on the Jupyter logo in the upper left corner. \n",
    "\n",
    "For this tutorial, we need to copy some files from this temporary folder to and from our workspace bucket. Run the commands below to set up environment variables and the file paths inside your notebook.\n",
    "\n",
    "<font color = \"green\"> **Tool Tip:** To run a cell in a notebook, press `SHIFT + ENTER`</font>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "VcIErgjx_sYu",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# Set your workspace bucket variable for this notebook.\n",
    "import os\n",
    "BUCKET = os.environ['WORKSPACE_BUCKET']\n",
    "\n",
    "# Set workshop variable to access the most recent materials\n",
    "WORKSHOP = \"workshop_1910\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "Mg-E9x9A_sYx",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# Create directories for your files to live inside this notebook\n",
    "! mkdir -p /home/jupyter-user/2-germline-vd/sandbox/\n",
    "! mkdir -p /home/jupyter-user/2-germline-vd/ref\n",
    "! mkdir -p /home/jupyter-user/2-germline-vd/resources\n",
    "! mkdir -p /home/jupyter-user/2-germline-vd/gvcfs\n",
    "! mkdir -p /home/jupyter-user/CNN/Output/"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "XzfJP4If_sY0"
   },
   "source": [
    "## Check data permissions\n",
    "For this tutorial, we have hosted the starting files in a public Google bucket. We will first check that the data is available to your user account, and if it is not, we simply need to install Google Cloud Storage."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 318
    },
    "colab_type": "code",
    "executionInfo": {
     "elapsed": 9902,
     "status": "ok",
     "timestamp": 1560183294278,
     "user": {
      "displayName": "Adelaide Rhodes",
      "photoUrl": "https://lh6.googleusercontent.com/-btsjdXqDOaw/AAAAAAAAAAI/AAAAAAAAAAc/bSfvkT4xjiw/s64/photo.jpg",
      "userId": "01268730178107877997"
     },
     "user_tz": 240
    },
    "id": "SjEiRqH4_sY0",
    "outputId": "15042217-97b7-4fa4-9d62-cb7bb175ce67",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# Check if data is accessible. The command should list several gs:// URLs.\n",
    "! gsutil ls gs://gatk-tutorials/$WORKSHOP/2-germline/"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "FbSTRvc0_sY2",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# If you do not see gs:// URLs listed above, uncomment the last line in this cell\n",
    "# and run it to install Google Cloud Storage. \n",
    "# Afterwards, restart the kernel with Kernel > Restart.\n",
    "#! pip install google-cloud-storage"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "I95K0qyU_sY4"
   },
   "source": [
    "## Download Data to the Notebook \n",
    "Some tools are not able to read directly from a Google bucket, so we download their files to our local notebook folder."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 478
    },
    "colab_type": "code",
    "executionInfo": {
     "elapsed": 16135,
     "status": "ok",
     "timestamp": 1560183314333,
     "user": {
      "displayName": "Adelaide Rhodes",
      "photoUrl": "https://lh6.googleusercontent.com/-btsjdXqDOaw/AAAAAAAAAAI/AAAAAAAAAAc/bSfvkT4xjiw/s64/photo.jpg",
      "userId": "01268730178107877997"
     },
     "user_tz": 240
    },
    "id": "GI122M4b_sY5",
    "outputId": "f398d31f-b117-40e4-fae8-e5d000bbb2d0",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gsutil cp gs://gatk-tutorials/$WORKSHOP/2-germline/ref/* /home/jupyter-user/2-germline-vd/ref\n",
    "! gsutil cp gs://gatk-tutorials/$WORKSHOP/2-germline/trio.ped /home/jupyter-user/2-germline-vd/\n",
    "! gsutil cp gs://gatk-tutorials/$WORKSHOP/2-germline/resources/* /home/jupyter-user/2-germline-vd/resources/\n",
    "! gsutil cp gs://gatk-tutorials/$WORKSHOP/2-germline/gvcfs/* /home/jupyter-user/2-germline-vd/gvcfs/"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Set up Integrative Genomics Viewer (IGV)\n",
    "We will be using IGV in this tutorial to view BAM and VCF files. In order to do so without downloading each individual file, we will connect IGV with our google account.\n",
    "- [Download IGV](https://software.broadinstitute.org/software/igv/download) to your local machine if you haven't already done so.\n",
    "- Follow [these instructions](https://googlegenomics.readthedocs.io/en/latest/use_cases/browse_genomic_data/igv.html) to connect your Google account to IGV.\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "msIkdvNu_sY8"
   },
   "source": [
    "-----------------------------------------------------------------------------------------------------------"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "QNgEG2X2_sY8"
   },
   "source": [
    "# Call variants with HaplotypeCaller in default VCF mode\n",
    "In this first step we run HaplotypeCaller in its simplest form on a single sample to get familiar with its operation and to learn some useful tips and tricks.  \n",
    "\n",
    "For this command and further commands in this tutorial, we will be working with data from the CEUTrio. The mother (NA12878) is used for our first command and is the most sequenced individual in the world. As such, she makes for a great case study to demonstrate how variant calling works, because we can verify the results against a larger body of knowledge. We will also be working with a father (NA12877) and a son (NA12882) in later portions of this notebook.\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 961
    },
    "colab_type": "code",
    "executionInfo": {
     "elapsed": 28124,
     "status": "ok",
     "timestamp": 1560184177526,
     "user": {
      "displayName": "Adelaide Rhodes",
      "photoUrl": "https://lh6.googleusercontent.com/-btsjdXqDOaw/AAAAAAAAAAI/AAAAAAAAAAc/bSfvkT4xjiw/s64/photo.jpg",
      "userId": "01268730178107877997"
     },
     "user_tz": 240
    },
    "id": "x7UaC1SO_sY9",
    "outputId": "c7c1a89b-28c7-433b-a303-2002fb0dd6fa",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gatk HaplotypeCaller \\\n",
    "    -R gs://gatk-tutorials/$WORKSHOP/2-germline/ref/ref.fasta \\\n",
    "    -I gs://gatk-tutorials/$WORKSHOP/2-germline/bams/mother.bam \\\n",
    "    -O /home/jupyter-user/2-germline-vd/sandbox/motherHC.vcf \\\n",
    "    -L 20:10,000,000-10,200,000"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "VJif-5iE_sZA",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# copy files from your notebook sandbox to your workspace bucket sandbox\n",
    "! gsutil cp /home/jupyter-user/2-germline-vd/sandbox/* $BUCKET/sandbox"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "GbAbNmB0_sZD"
   },
   "source": [
    "Open IGV and <font color=red>set the genome to b37</font>. It is important you do this first, as changing the genome later will require you to reopen all files you may have already loaded into the program. \n",
    "\n",
    "Load the input BAM (mother.bam) and output VCF (mother.vcf), both printed below, in IGV and go to the coordinates **20:10,002,294-10,002,623**."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "CAgsSVon_sZD",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# prints out the file paths you will need to open in IGV\n",
    "! echo gs://gatk-tutorials/$WORKSHOP/2-germline/bams/mother.bam\n",
    "! echo $BUCKET/sandbox/motherHC.vcf"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "Hq4HXZDV_sZF"
   },
   "source": [
    "We see that HaplotypeCaller called a homozygous variant insertion of three T bases. How is this possible when so few reads seem to support an insertion at this position? When you encounter indel-related weirdness, turn on the display of soft-clips, which IGV turns off by default. Go to View > Preferences > Alignments and select “Show soft-clipped bases”.\n",
    "\n",
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image1-IGVDesktop.png\" alt=\"drawing\" width=\"60%\"/>\n",
    "\n",
    "With soft clip display turned on, the region lights up with mismatching bases. **For these reads, the aligner (BWA MEM in our case) found the penalty of soft-clipping mismatching bases less than the penalty of inserting bases or inserting a gap.**\n",
    "\n",
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image2-IGVDesktop.png\" alt=\"drawing\" width=\"100%\"/>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<font color=green>**Tool Tip**</font>\n",
    "\n",
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image3-IGVDesktop.png\" alt=\"drawing\" width=\"25px\" align=left style=\"margin:20px 10px\">\n",
    "\n",
    "By default, IGV shows details of each read when you hover over them. To change this, click on the yellow box icon in the top bar and select `Show Details on Click`.\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "BBrmheMG_sZG"
   },
   "source": [
    "## View realigned reads and assembled haplotypes\n",
    "Let's take a peek under the hood of HaplotypeCaller. HaplotypeCaller has a parameter called `-bamout`, which allows you to ask for the realigned reads. **These realigned reads are what HaplotypeCaller uses to make its variant calls**, so you will be able to see if a realignment fixed the messy region in the original bam.\n",
    "\n",
    "Run the following command:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "7SKNby5J_sZH",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gatk HaplotypeCaller \\\n",
    "    -R gs://gatk-tutorials/$WORKSHOP/2-germline/ref/ref.fasta \\\n",
    "    -I gs://gatk-tutorials/$WORKSHOP/2-germline/bams/mother.bam \\\n",
    "    -O /home/jupyter-user/2-germline-vd/sandbox/motherHCdebug.vcf \\\n",
    "    -bamout /home/jupyter-user/2-germline-vd/sandbox/motherHCdebug.bam \\\n",
    "    -L 20:10,002,000-10,003,000"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "oF9WzYLA_sZI",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# copy files from your notebook sandbox to your workspace bucket sandbox\n",
    "! gsutil cp /home/jupyter-user/2-germline-vd/sandbox/* $BUCKET/sandbox"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "fdevgLdr_sZK"
   },
   "source": [
    "Load the output BAM (motherHCdebug.bam) in IGV, and switch to Collapsed view (right-click>Collapsed). You should still be zoomed in on the same coordinates (**20:10,002,294-10,002,623**), and have the mother.bam track loaded for comparison."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "z8kZyItz_sZL",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# prints out the file paths you will need to open in IGV\n",
    "! echo $BUCKET/sandbox/motherHCdebug.bam"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "SL6MS8SG_sZN"
   },
   "source": [
    "Since we are only interested in looking at that messy region, we gave the tool a narrowed interval with `-L 20:10,002,000-10,003,000`. This is why the reads seem to sharply cut off when you compare the original BAM with the realigned BAM.\n",
    "\n",
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image4-IGVDesktop.png\" alt=\"drawing\" width=\"100%\"/>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "C-i0J6MT_sZN"
   },
   "source": [
    "After realignment by HaplotypeCaller (the bottom track), almost all the reads show the insertion, and the messy soft clips from the original bam are gone. **HaplotypeCaller will utilize soft-clipped sequences towards realignment**. Expand the reads in the output BAM (right-click>Expanded view), and you can see that all the insertions are in phase with the C/T SNP. \n",
    "\n",
    "This shows that HaplotypeCaller found a different alignment after performing its local graph assembly step. The reassembled region provided HaplotypeCaller with enough support to call the indel, which position-based callers like UnifiedGenotyper would have missed.\n",
    "\n",
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image5-IGVDesktop.png\" alt=\"drawing\" width=\"60%\"/>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "mr_kAaSW_sZO"
   },
   "source": [
    "➤ Focus on the insertion locus. **How many different types of insertions do you see?** Which one did HaplotypeCaller call in the VCF? What do you think of this choice?\n",
    "\n",
    "There is more to a BAM than meets the eye--or at least, what you can see in this view of IGV. Right-click on the motherHCdebug.bam track to bring up the view options menu. **Select Color alignments by, and choose read group.** Your gray reads should now be colored similar to the screenshot below.\n",
    "\n",
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image6-IGVDesktop.png\" alt=\"drawing\" width=\"60%\"/>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "HixROuj6_sZO"
   },
   "source": [
    "Some of the first reads, shown in **red at the top of the pile, are not real reads.** These represent artificial haplotypes that were constructed by HaplotypeCaller, and are tagged with a special read group identifier, **RG:Z:ArtificialHaplotypeRG** to differentiate them from actual reassembled reads. You can click on an artificial read to see this tag under Read Group. "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "IvCtLFG1_sZP"
   },
   "source": [
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image7-IGVDesktop.png\" alt=\"drawing\" width=\"40%\" align=left style=\"margin:0px 20px\"/> \n",
    "\n",
    "<br>\n",
    "➤ How are each of the three artificial haplotypes different from the others? \n",
    "\n",
    "Let's separate these artificial reads to the top of the track. Right click on a read, then select **Sort alignments by**, and choose **base**.\n",
    "\n",
    "If you click on the purple insertion bars, you can see what call they correspond to. There is a `TTT` insertion and a `TT` insertion. When we sort by base, it will push the reads with evidence for a `TTT` insertion up to the top."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "IvCtLFG1_sZP"
   },
   "source": [
    "\n",
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image8-IGVDesktop.png\" alt=\"drawing\" width=\"50%\" align=left style=\"margin:20px 20px\"/>\n",
    "\n",
    "Now we will color the reads differently. Right click on a read again and select **Color alignments by**, choose **tag**, and type in **HC**. HaplotypeCaller labels reassembled reads that have unequivocal support for a haplotype (based on likelihood calculations) with an HC tag value that matches the HC tag value of the corresponding haplotype. The gray color on some reads indicate that they could support one or more possible haplotypes.\n",
    "\n",
    "\n",
    "\n",
    "➤ Again, what do you think of HaplotypeCaller's choice to call the three-base insertion instead of the two-base insertion? Is there more evidence for one or the other?\n",
    "\n",
    "If you zoom out, you will also see the three active regions within the scope of the interval we provided. HaplotypeCaller considered twelve, three, and six putative haplotypes, respectively, for the regions, and performed local reassembly for each of the three regions. "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "4Jpw6WSt_sZQ"
   },
   "source": [
    "-----------------------------------------------------------------------------------------------------------"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "PJmwn4aY_sZR"
   },
   "source": [
    "# GVCF workflow"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "Iu6orTDv_sZR"
   },
   "source": [
    "## Run HaplotypeCaller on a single bam file in GVCF mode\n",
    "\n",
    "It is possible to genotype a multi-sample cohort simultaneously with HaplotypeCaller. However, this scales poorly. **For a scalable analysis, GATK offers the GVCF workflow**, which separates BAM-level variant calling from genotyping. In the GVCF workflow, HaplotypeCaller is run with the `-ERC GVCF` option on each individual BAM file and produces a GVCF, which adheres to VCF format specifications while giving information about the data at every genomic position. GenotypeGVCFs then genotypes the samples in a cohort via the given GVCFs.\n",
    "\n",
    "Run HaplotypeCaller in GVCF mode on the mother’s bam. This will produce a GVCF file that contains likelihoods for each possible genotype for the variant alleles, including a symbolic <NON_REF> allele. You'll see what this looks like soon."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "T7kzv1sH_sZS",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gatk HaplotypeCaller \\\n",
    "    -R gs://gatk-tutorials/$WORKSHOP/2-germline/ref/ref.fasta \\\n",
    "    -I gs://gatk-tutorials/$WORKSHOP/2-germline/bams/mother.bam \\\n",
    "    -O /home/jupyter-user/2-germline-vd/sandbox/mother.g.vcf \\\n",
    "    -ERC GVCF \\\n",
    "    -L 20:10,000,000-10,200,000"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "bRITcPXe_sZU",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# copy files from your notebook sandbox to your workspace bucket sandbox\n",
    "! gsutil cp /home/jupyter-user/2-germline-vd/sandbox/* $BUCKET/sandbox"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "5Ua1LiuB_sZW"
   },
   "source": [
    "**In the interest of time, we have supplied the other sample GVCFs in the bundle, but normally you would run them individually in the same way as the first.**\n",
    "\n",
    "Let's take a look at a GVCF in IGV. Start a new session to clear your IGV screen (File>New Session), then load the GVCF for each family member, printed with the command below. Zoom in on **20:10,002,371-10,002,546**."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "8WZSnOie_sZX",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# prints out the file paths you will need to open in IGV\n",
    "! echo gs://gatk-tutorials/$WORKSHOP/2-germline/gvcfs/father.g.vcf.gz\n",
    "! echo $BUCKET/sandbox/mother.g.vcf\n",
    "! echo gs://gatk-tutorials/$WORKSHOP/2-germline/gvcfs/son.g.vcf.gz"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "ou7rStjK_sZa"
   },
   "source": [
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image9-IGVDesktop.png\" alt=\"drawing\" width=\"100%\"/>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "PYELQOcQ_sZb"
   },
   "source": [
    "Notice anything different from the VCF? Along with the colorful variant sites, you see many gray blocks in the GVCF representing reference confidence intervals. The gray blocks represent the blocks where the sample **appears** to be **homozygous reference or invariant**. The likelihoods are evaluated against an abstract non-reference allele and so these are referred to somewhat **counterintuitively as NON_REF** blocks of the GVCF. Each belongs to different **contiguous quality GVCFBlock** blocks. \n",
    "\n",
    "If we peek into the GVCF file using the command below, we actually see in the ALT column a **symbolic <NON_REF> allele, which represents non-called but possible non-reference alleles**. Using the likelihoods against the <NON_REF> allele we assign likelihoods to alleles that weren’t seen in the current sample during joint genotyping. Additionally, for NON_REF blocks, the **INFO field gives the end position** of the homozygous-reference block. The **FORMAT field gives Phred-scaled likelihoods (PL) for each potential genotype** given the alleles including the NON_REF allele.\n",
    "\n",
    "Later, the genotyping step will retain only sites that are confidently variant against the reference. \n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "!head -n100 /home/jupyter-user/2-germline-vd/sandbox/mother.g.vcf"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "0oFkVkw1_sZb"
   },
   "source": [
    "## Consolidate GVCFs using GenomicsDBImport\n",
    "For the next step, we need to consolidate the GVCFs into a GenomicsDB datastore. That might sound complicated but it's actually very straightforward."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "PHuxE_XU_sZc",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! rm -rf /home/jupyter-user/2-germline-vd/sandbox/trio"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "lAeh72dj_sZe",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gatk GenomicsDBImport \\\n",
    "    -V gs://gatk-tutorials/$WORKSHOP/2-germline/gvcfs/mother.g.vcf.gz \\\n",
    "    -V gs://gatk-tutorials/$WORKSHOP/2-germline/gvcfs/father.g.vcf.gz \\\n",
    "    -V gs://gatk-tutorials/$WORKSHOP/2-germline/gvcfs/son.g.vcf.gz \\\n",
    "    --genomicsdb-workspace-path /home/jupyter-user/2-germline-vd/sandbox/trio \\\n",
    "    --intervals 20:10,000,000-10,200,000"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "z70HWc0o_sZf"
   },
   "source": [
    "For those who cannot use GenomicDBImport, the alternative is to consolidate GVCFs with CombineGVCFs. Keep in mind though that the GenomicsDB intermediate allows you to scale analyses to large cohort sizes efficiently, and to add data incremently (which is not possible in CombineGVCFs). **Because it's not trivial to examine the data within the database, we will extract the trio's combined data from the GenomicsDB database using SelectVariants.**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "Ue3yPP-J_sZg",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# Create a soft link to sandbox.\n",
    "! rm -f sandbox\n",
    "! ln -s /home/jupyter-user/2-germline-vd/sandbox/ sandbox"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "T8vs84Co_sZi",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gatk SelectVariants \\\n",
    "    -R /home/jupyter-user/2-germline-vd/ref/ref.fasta \\\n",
    "    -V gendb://sandbox/trio \\\n",
    "    -O /home/jupyter-user/2-germline-vd/sandbox/trio_selectvariants.g.vcf"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "lnkBLr0g_sZm"
   },
   "source": [
    "➤ Take a look inside the combined GVCF. How many samples are represented? What is going on with the genotype field (GT)? What does this genotype notation mean?"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "VQjIxKGZ_sZm",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! cat /home/jupyter-user/2-germline-vd/sandbox/trio_selectvariants.g.vcf | grep -v '#' | head"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "F_dbLOnE_sZo"
   },
   "source": [
    "## Run joint genotyping on the trio to generate the VCF\n",
    "The last step is to joint genotype variant sites for the samples using GenotypeGVCFs. "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "6kEpRC1b_sZo",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gatk GenotypeGVCFs \\\n",
    "    -R /home/jupyter-user/2-germline-vd/ref/ref.fasta \\\n",
    "    -V gendb://sandbox/trio \\\n",
    "    -O /home/jupyter-user/2-germline-vd/sandbox/trioGGVCF.vcf \\\n",
    "    -L 20:10,000,000-10,200,000"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "jDQcLTlS_sZq",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# copy files from your notebook sandbox to your workspace bucket sandbox\n",
    "! gsutil cp /home/jupyter-user/2-germline-vd/sandbox/* $BUCKET/sandbox"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "vJx9S4HF_sZu"
   },
   "source": [
    "The calls made by GenotypeGVCFs and HaplotypeCaller run in multisample mode should mostly be equivalent, especially as cohort sizes increase. However, there can be some marginal differences in borderline calls, i.e. low-quality variant sites, in particular for small cohorts with low coverage. For such cases, joint genotyping directly with HaplotypeCaller and/or using the new quality score model with GenotypeGVCFs (turned on with `-new-qual`) may be preferable.\n",
    "\n",
    "```\n",
    "gatk HaplotypeCaller \\\n",
    "    -R ref/ref.fasta \\\n",
    "    -I bams/mother.bam \\\n",
    "    -I bams/father.bam \\\n",
    "    -I bams/son.bam \\\n",
    "    -O sandbox/trio_hcjoint_nq.vcf \\\n",
    "    -L 20:10,000,000-10,200,000 \\\n",
    "    -new-qual \\\n",
    "    -bamout sandbox/trio_hcjoint_nq.bam\n",
    "```\n",
    "\n",
    "In the interest of time, we do not run the above command. Note the BAMOUT will contain reassembled reads for all the input samples. \n",
    "\n",
    "Let's circle back to the locus we examined at the start. Load sandbox/trioGGVCF.vcf into IGV and navigate to <b>20:10,002,376-10,002,550</b>."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "ljqkM5cO_sZu",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# prints out the file paths you will need to open in IGV\n",
    "! echo $BUCKET/sandbox/trioGGVCF.vcf"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "_grivpf4_sZv"
   },
   "source": [
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image10-IGVDesktop.png\" alt=\"drawing\" width=\"50%\"/>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "_grivpf4_sZv"
   },
   "source": [
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image11-IGVDesktop.png\" alt=\"drawing\" width=\"20%\" align=right style=\"margin:20px 20px\"/>\n",
    "\n",
    "Take a look at the father's genotype call at **20:10002458** (the leftmost variant call). Knowing the familial relationship for the three samples and the child's homozygous-variant genotype, what do you think about the father's HOM_REF call?\n",
    "\n",
    "Results from GATK v4.0.1.0 also show HOMREF but give PLs (phred-scaled likelihoods) of 0,0,460. Changes since then improve hom-ref GQs near indels in GVCFs, as seen in the results from GATK v4.1.1.0 in the picture on the right. The table below shows this is an ambiguous site for other callers as well. \n",
    "\n",
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image3.png\" alt=\"drawing\" width=\"60%\" align=left style=\"margin:0px 20px\"/> "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "If you recall the pipeline at the top of this notebook, you'll remember that there are several post-processing steps after we get raw variant calls. It's possible that those filtering steps would improve the call to resolve the Mendelian inheritance violation, but we don't have time to look into that further today.\n",
    "\n",
    "Now let's take a look at the father's other variant call at **20:10002470** (the rightmost one). It also doesn't follow familial inheritance rules, but if you click on that site you'll notice something very interesting. The genotype is marked as `./.` and the PL is `0,0,0`. This indicates that HaplotypeCaller emitted **no call** at that location--it did not find evidence for either a reference call or a variant call for the father.\n",
    "\n",
    "This is a great candidate for genotype refinement."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "NJhUfYUz_sZw"
   },
   "source": [
    "------------------------------------------------------------------------------------"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "LcgbCe_1_sZw"
   },
   "source": [
    "# Genotype Refinement"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "gmQGbP1z_sZx"
   },
   "source": [
    "## Refine the genotype calls with CalculateGenotypePosteriors\n",
    "If you are running this notebook as a part of the GATK workshop series, then you will shortly hear more about Genotype Refinement. The basic principle is that we can systematically refine our calls for the trio using a tool called CalculateGenotypePosteriors. For starters, we can use pedigree information, which is provided in the trio.ped file. Second, we can use population priors; we use a population allele frequencies resource derived from gnomAD."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "TJDAxfH-_sZy",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gatk CalculateGenotypePosteriors \\\n",
    "    -V /home/jupyter-user/2-germline-vd/sandbox/trioGGVCF.vcf \\\n",
    "    -ped /home/jupyter-user/2-germline-vd/trio.ped \\\n",
    "    --skip-population-priors \\\n",
    "    -O /home/jupyter-user/2-germline-vd/sandbox/trioCGP.vcf"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "mEBVXsvp_sZ0",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gatk CalculateGenotypePosteriors \\\n",
    "    -V /home/jupyter-user/2-germline-vd/sandbox/trioGGVCF.vcf \\\n",
    "    -ped /home/jupyter-user/2-germline-vd/trio.ped \\\n",
    "    --supporting-callsets /home/jupyter-user/2-germline-vd/resources/af-only-gnomad.chr20subset.b37.vcf.gz \\\n",
    "    -O /home/jupyter-user/2-germline-vd/sandbox/trioCGP_gnomad.vcf"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "PMO60gT__sZ2",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# copy files from your notebook sandbox to your workspace bucket sandbox\n",
    "! gsutil cp /home/jupyter-user/2-germline-vd/sandbox/* $BUCKET/sandbox"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "SBXk9uS2_sZ3",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# prints out the file paths you will need to open in IGV\n",
    "! echo $BUCKET/sandbox/trioCGP.vcf\n",
    "! echo $BUCKET/sandbox/trioCGP_gnomad.vcf"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "1y_vMuXU_sZ4"
   },
   "source": [
    "<img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image12-IGVDesktop.png\" alt=\"drawing\" width=\"30%\" align=right style=\"margin:0px 20px\"/> Add both sandbox/trioCGP.vcf and sandbox/trioCGP_gnomad.vcf to the IGV session. \n",
    "\n",
    "➤ What has changed? What has not changed?\n",
    "\n",
    "You'll notice that the difficult-to-call site on the left (position 10002458) hasn't adjusted its calls at all, but it has become a lot less confident in its call. Compare the GQ values, and you'll see that it's confidence in that G/G call is much lower-- from 42 to 2. A GQ of 2 is a site that would certainly be filtered out in post-processing.\n",
    "\n",
    "CalculateGenotypePosteriors adds the Phred-scaled Posterior Probability (**PP**), which basically refines the PL values. It incorporates the prior expectations for the given pedigree and/or population allele frequencies. Compare the PP and PL of the final gnomad file, and you'll see that there was another haplotype it ranked at a likelihood of 4. This means this site is pretty closely torn between 3 different possible haplotypes.\n",
    "\n",
    "On the other hand, the ambiguous site on the right (position 10002470) was improved as we had predicted! With information from both the population priors and pedigree data, the father's new variant call at that site is `HOM_REF` with a genotype quality of 72. This is now a confident `HOM_REF` call.\n",
    "\n",
    "The PL stays the same, still calling 0,0,0. If you add to the cohort again in the future, you'll be able to re-evaluate. In our case, it looks like CalculateGenotypePosteriors found that the population, including the family, had a high frequency for the T allele at this site."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "Ok1EaBJa_sZ5"
   },
   "source": [
    " <img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image13-IGVDesktop.png\" alt=\"drawing\" width=\"43%\" align=left style=\"margin:0px 20px\"/> <img src=\"https://storage.googleapis.com/gatk-tutorials/images/2-germline/vd-image14-IGVDesktop.png\" alt=\"drawing\" width=\"43%\" align=left style=\"margin:0px 20px\"/> "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "You can learn more about the Genotype Refinement workflow [here](https://software.broadinstitute.org/gatk/documentation/article?id=11074).  "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "4sD0IyWa_sZ5"
   },
   "source": [
    "## Compare changes with CollectVariantCallingMetrics \n",
    "There are a few different GATK/Picard tools to compare site-level and genotype-level concordance. If you are in a GATK workshop while running this tutorial, you will see the presentation soon. If you aren't, here's a quick summary. `CollectVariantCallingMetrics` collects summary and per-sample metrics about variant calls in a VCF file. We are going to compare our callsets before and after Genotype Refinement to see if we've improved them overall."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "2DJNxrYJ_sZ6",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gatk CollectVariantCallingMetrics \\\n",
    "    -I /home/jupyter-user/2-germline-vd/sandbox/trioGGVCF.vcf \\\n",
    "    --DBSNP /home/jupyter-user/2-germline-vd/resources/dbsnp.vcf \\\n",
    "    -O /home/jupyter-user/2-germline-vd/sandbox/trioGGVCF_metrics"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "YsdzBx-P_sZ7",
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "! cat /home/jupyter-user/2-germline-vd/sandbox/trioGGVCF_metrics.variant_calling_detail_metrics | grep -v \"##\" | grep -v \"#\" | cut -f1,6,11,13,18 \n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "QgFZNhvG_sZ9",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! gatk CollectVariantCallingMetrics \\\n",
    "    -I /home/jupyter-user/2-germline-vd/sandbox/trioCGP.vcf \\\n",
    "    --DBSNP /home/jupyter-user/2-germline-vd/resources/dbsnp.vcf \\\n",
    "    -O /home/jupyter-user/2-germline-vd/sandbox/trioCGP_metrics"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "URGyc4VU_sZ-",
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "! cat /home/jupyter-user/2-germline-vd/sandbox/trioCGP_metrics.variant_calling_detail_metrics | grep -v \"##\" | grep -v \"#\" | cut -f1,6,11,13,18 \n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "A_mHcvvE_saA"
   },
   "source": [
    "CollectVariantCallingMetrics produces both summary and detail metrics. The summary metrics provide cohort-level variant metrics, while the detail metrics segment the variant metrics for each sample in the callset, and add a few more fields. (You can read about all metrics more in-depth [here](https://broadinstitute.github.io/picard/picard-metric-definitions.html).)\n",
    "\n",
    "For our purposes, we have subset the detailed metrics to a smaller number of columns to discuss here.\n",
    "\n",
    "**Total SNPS and Total INDELS**\n",
    "Comparing the two files, you will see that we recovered 3 SNP sites in the mother (NA12878) and 4 in the father (NA12887). We also recovered indels for each of the three samples.\n",
    "\n",
    "**DBSNP_TITV**\n",
    "This column shows the transition (Ti) transversion(Tv) ratio. In whole-genome samples, we expect the ratio to be between 2 and 2.1. We see a slight improvement in this ratio for the father (NA12877) and the mother (NA12878), but they are still below 2, which could indicate a higher rate of false positives in the callset. Further filtering would improve this score.\n",
    "\n",
    "**DBNSP_INS_DEL_RATIO**\n",
    "This column shows the ratio of insertions to deletions, which we expect to be about 1 for common variant studies. As we haven't specifically picked these samples to diagnose a rare disease, common variation has equal selective pressure on insertion and deletion events, so we find those to be about even. In rare disease, we often see a ratio of 0.2-0.5. Our results show that the numbers stay about the same or increase very slightly. It's not a strong indicator of success, but it does show that we didn't completely imbalance the callset by applying Genotype Refinement to fix those two odd sites."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "colab": {
   "collapsed_sections": [
    "BBrmheMG_sZG",
    "Iu6orTDv_sZR",
    "0oFkVkw1_sZb",
    "F_dbLOnE_sZo",
    "gmQGbP1z_sZx",
    "4sD0IyWa_sZ5"
   ],
   "name": "Copy of 1-gatk-germline-variant-discovery-tutorial.ipynb",
   "provenance": [
    {
     "file_id": "1VFcu-Jr9oRnvSbrLiQZpBPyz-ql5EyhJ",
     "timestamp": 1560184402246
    }
   ],
   "toc_visible": true,
   "version": "0.3.2"
  },
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.8"
  },
  "toc": {
   "base_numbering": 1,
   "nav_menu": {
    "height": "304px",
    "width": "424px"
   },
   "number_sections": true,
   "sideBar": true,
   "skip_h1_title": false,
   "title_cell": "Table of Contents",
   "title_sidebar": "Contents",
   "toc_cell": false,
   "toc_position": {
    "height": "calc(100% - 180px)",
    "left": "10px",
    "top": "150px",
    "width": "343.594px"
   },
   "toc_section_display": true,
   "toc_window_display": true
  }
 },
 "nbformat": 4,
 "nbformat_minor": 1
}
