/*******************************************************************************
 *  jUnit Artifact Needed For Testing Categories
 *******************************************************************************/
package categories;

// NLP Insights Tests
import org.junit.experimental.categories.Categories;
import org.junit.runner.RunWith;
import org.junit.runners.Suite.SuiteClasses;

@RunWith(Categories.class)
@SuiteClasses(AllTests.class) 
@Categories.IncludeCategory(NLPEnrichmentFVT.class)

public class NLPEnrichmentFVTTests {
 
}
